# 01 – Workflow Orchestration in Python (Airflow & Co.)

**Level:** Master's degree (Data Engineering / MLOps / Big Data)
**Duration:** 60 minutes (≈ 25 min lecture + 30 min hands-on + 5 min wrap-up)
**Companion notebook:** `01_orchestration.ipynb`
**Prerequisites:** Python (functions, decorators, `datetime`), basic SQL/ETL notions, command line

---

## Learning objectives

By the end of this session, students can:

1. **Define** orchestration and distinguish it from scheduling, ETL tools and streaming.
2. **Model** a pipeline as a DAG and reason about dependencies, retries, idempotency and backfills.
3. **Explain** the architecture of Apache Airflow (scheduler, executor, workers, metadata DB, API server / webserver, triggerer, dag-processor).
4. **Write** a production-style Airflow DAG with the TaskFlow API, dynamic task mapping and trigger rules.
5. **Compare** Airflow with Prefect, Dagster, Luigi, Argo/Kubeflow and Temporal, and **choose** a tool for a given scenario.

---

## Session plan (60 min)

| Time | Block | Format |
|------|-------|--------|
| 0–8 | 1. Why orchestration? | Lecture + live failure demo |
| 8–15 | 2. Core concepts (DAG, idempotency, backfill, retries) | Lecture |
| 15–30 | 3. Apache Airflow in depth | Lecture + code |
| 30–38 | 4. Landscape: Prefect, Dagster, Luigi, Argo, Temporal | Lecture / discussion |
| 38–55 | 5. Hands-on: build a mini-orchestrator, then a real Airflow DAG | Notebook |
| 55–60 | 6. Wrap-up, quiz, take-home work | Interactive |

---

## 1. Why orchestration? (8 min)

### The problem
A "pipeline" quickly becomes a set of scripts glued by `cron`:

```
0 2 * * *  python extract.py
30 2 * * * python transform.py     # hope extract finished...
0 3 * * *  python load.py          # hope transform finished...
```

Failure modes of this approach:

- **Implicit dependencies** – timing guesses instead of explicit ordering.
- **No retries / alerting** – failure is discovered by a stakeholder, not by the system.
- **No history** – what ran, when, how long, with which parameters?
- **No backfill** – re-processing last month means manual shell loops.
- **No parallelism / resource control** – everything runs on one machine, or all at once.

### Definition
> **Orchestration** = defining, scheduling, executing, monitoring and recovering *dependent* tasks across systems, automatically and reproducibly.

| Concept | Does | Example |
|---|---|---|
| Scheduler (cron) | Triggers a command at a time | `cron`, `systemd timers` |
| **Orchestrator** | Manages dependencies, state, retries, history | Airflow, Prefect, Dagster |
| Processing engine | Does the heavy computation | Spark, dbt, pandas, SQL warehouse |
| Streaming engine | Continuous, low-latency processing | Kafka Streams, Flink |

**Key principle:** *the orchestrator orchestrates, it does not compute.* Heavy work is delegated to Spark, a warehouse, a container, etc.

---

## 2. Core concepts (7 min)

### 2.1 DAG – Directed Acyclic Graph
- **Nodes** = tasks; **edges** = dependencies ("B runs after A").
- **Acyclic** = no cycles, so a valid execution order exists (topological order).
- Python's standard library already ships a solver: `graphlib.TopologicalSorter`.

```
extract_eu ─┐
extract_us ─┼─> transform ─> load ─> notify
extract_ap ─┘
```

### 2.2 Task states
`queued → running → success | failed | up_for_retry | upstream_failed | skipped`

### 2.3 Idempotency (the most important property)
A task is **idempotent** if running it N times with the same input gives the same result as running it once.

- ❌ `INSERT INTO sales SELECT ... WHERE day = today` (duplicates on retry)
- ✅ `DELETE ... WHERE day = :ds; INSERT ...` or `MERGE`/`UPSERT`, or overwrite partition `sales/ds=2025-01-01/`

Related rules: **atomic** tasks (all-or-nothing), **no hidden state**, **parametrize by logical date, never by `now()`**.

### 2.4 Data interval & logical date
A daily run labelled `2025-01-01` processes data from `2025-01-01 00:00` to `2025-01-02 00:00` and **starts after the interval ends**. The run is identified by its *logical date* (`ds`), not by wall-clock time. This is what makes **backfills** and **reruns** reproducible.

### 2.5 Retries, timeouts, SLAs
Retries with exponential backoff handle transient errors (network, rate limits). Timeouts prevent zombie tasks. Alerts/callbacks notify humans only when automation gives up.

### 2.6 Backfill & catchup
Re-running the pipeline for a past range of logical dates (new logic, bug fix, new source). Works only if tasks are idempotent and parametrized by logical date.

---

## 3. Apache Airflow in depth (15 min)

Created at Airbnb (2014), Apache top-level project (2019). **Workflows as code in Python.** Airflow 3.x (2025+) is the current major line.

### 3.1 Architecture

```
┌────────────┐   parse    ┌──────────────┐
│ DAG files  │──────────▶ │ DAG processor│
└────────────┘            └──────┬───────┘
                                 │ serialized DAGs
                         ┌───────▼────────┐        ┌───────────────┐
 Users ─▶ UI / API ─────▶│  Metadata DB   │◀──────▶│   Scheduler   │
 server                  │ (Postgres)     │        └──────┬────────┘
                         └───────▲────────┘               │ queue tasks
                                 │ state                  ▼
                         ┌───────┴────────┐        ┌───────────────┐
                         │    Workers     │◀───────│   Executor    │
                         └────────────────┘        │ Local/Celery/ │
                                                   │ Kubernetes    │
                                                   └───────────────┘
          Triggerer: runs async "deferrable" operators (waits without holding a worker slot)
```

| Component | Role |
|---|---|
| **DAG processor** | Parses Python files, stores serialized DAGs |
| **Scheduler** | Decides which task instances are ready, creates runs |
| **Executor** | *How/where* tasks run: `LocalExecutor`, `CeleryExecutor`, `KubernetesExecutor` |
| **Workers** | Actually execute task code |
| **Metadata DB** | Single source of truth for state (use Postgres in prod, never SQLite) |
| **API server / UI** | Monitoring, triggering, logs (Airflow 3: new React UI + REST API; task code talks to the API via the Task SDK) |
| **Triggerer** | Event loop for deferrable operators/sensors |

> Airflow 2 → 3 notes: imports move to `airflow.sdk` (`from airflow.sdk import dag, task`); `schedule_interval` and `execution_date` are removed (use `schedule`, `logical_date`); `catchup` defaults to `False`; *Datasets* become *Assets*.

### 3.2 A modern DAG (TaskFlow API)

```python
import pendulum
from airflow.sdk import dag, task      # Airflow 2.x: from airflow.decorators import dag, task

@dag(
    dag_id="sales_etl",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    default_args={"retries": 2},
    tags=["course"],
)
def sales_etl():

    @task
    def list_regions() -> list[str]:
        return ["eu", "us", "apac"]

    @task
    def extract(region: str) -> dict:
        ...
        return {"region": region, "rows": 123}

    @task
    def load(batches: list[dict]) -> int:
        return sum(b["rows"] for b in batches)

    batches = extract.expand(region=list_regions())   # dynamic task mapping
    load(batches)

sales_etl()
```

### 3.3 Key building blocks

| Feature | What it gives you |
|---|---|
| **Operators** | Reusable task templates: `BashOperator`, `SQLExecuteQueryOperator`, `KubernetesPodOperator`, provider operators for Spark, dbt, BigQuery, S3… |
| **TaskFlow (`@task`)** | Python functions as tasks; return values passed automatically via XCom |
| **XCom** | Small metadata between tasks (KBs!). **Never pass DataFrames** – pass paths/URIs |
| **Sensors / Deferrable operators** | Wait for a file, partition, API state without wasting worker slots |
| **Dynamic task mapping** (`.expand`) | Fan-out at runtime based on data (one task per file/region/partition) |
| **Trigger rules** | `all_success` (default), `all_done`, `one_failed`, `none_failed`… for cleanup/alert tasks |
| **Pools / concurrency** | Protect databases and APIs (`pool`, `max_active_tasks`, `max_active_runs`) |
| **Connections & Variables / Secrets backends** | Credentials outside the code |
| **Assets (ex-Datasets)** | Data-aware scheduling: "run when upstream data is updated" |
| **Params & templating (Jinja)** | `{{ ds }}`, `{{ data_interval_start }}` in SQL/bash |
| **Callbacks / SLAs / alerts** | `on_failure_callback`, email, Slack |

### 3.4 Airflow best practices
1. Idempotent, atomic, parametrized tasks.
2. **Top-level DAG code must be cheap**: no DB/API calls at import time (the file is parsed constantly).
3. Delegate heavy compute; keep tasks short and orchestration-only.
4. Pass **references** (S3 path, table name) via XCom, not data.
5. Use `retries` + `retry_exponential_backoff`, set `execution_timeout`.
6. Keep DAGs in Git, test in CI (`DagBag` import test, unit tests on task functions).
7. Never use `datetime.now()` inside tasks for business logic.
8. Pin versions (use official constraint files when installing).

### 3.5 Typical Airflow weaknesses
- Not designed for event-driven / low-latency / streaming workloads.
- Local dev and testing used to be heavy (improved in v3).
- Operational burden (scheduler, DB, executor tuning) – hence managed offerings (MWAA, Cloud Composer, Astronomer).

---

## 4. The Python orchestration landscape (8 min)

| Tool | Paradigm | Strengths | Watch out |
|---|---|---|---|
| **Airflow** | Task-centric DAGs, scheduled | Huge ecosystem of providers, mature, industry standard | Ops overhead, schedule-oriented |
| **Prefect** | Python-first flows, dynamic, event-driven | Very low boilerplate, native dynamic workflows, easy local run | Smaller provider ecosystem |
| **Dagster** | **Asset-centric** (data assets, lineage) | Software-defined assets, typed IO, great testing & lineage, dbt integration | Different mental model |
| **Luigi** (Spotify) | Target-based pipelines | Simple, file-target dependency model | Dated, no built-in scheduler, small community |
| **Argo Workflows / Kubeflow Pipelines** | Container/K8s-native YAML or SDK | Great for ML on Kubernetes | Requires K8s |
| **Temporal / Celery** | Durable execution / task queue | Long-running business processes, exactly-once semantics | Not data-pipeline oriented |
| **dbt (+ Cosmos)** | SQL transformation DAG | In-warehouse transforms | Not a general orchestrator |

### Same tiny pipeline in three styles

```python
# Airflow (task-centric)
@task
def extract(): ...
@task
def load(x): ...
load(extract())
```

```python
# Prefect (flow = plain Python)
from prefect import flow, task

@task(retries=3, retry_delay_seconds=10)
def extract(): ...

@flow
def etl():
    data = extract()
    load(data)

etl()          # runs locally, no server needed
```

```python
# Dagster (asset-centric: you declare the *data*, not the steps)
from dagster import asset, Definitions

@asset
def raw_sales(): ...

@asset
def clean_sales(raw_sales): ...

defs = Definitions(assets=[raw_sales, clean_sales])
```

### Decision guide
- Large org, many heterogeneous systems, need standard → **Airflow**.
- Python-heavy team, dynamic/event-driven flows, fast iteration → **Prefect**.
- Analytics engineering, lineage and data quality first → **Dagster**.
- ML training on Kubernetes → **Argo / Kubeflow**.
- Business processes with long waits/human-in-the-loop → **Temporal**.

---

## 5. Hands-on (17 min) – see `01_orchestration.ipynb`

| Step | Time | What you do |
|---|---|---|
| A | 3 min | Experience a failing "naive" pipeline |
| B | 6 min | Build a **mini-orchestrator** (~60 lines): topological sort, parallelism, retries with backoff, upstream-failed propagation |
| C | 3 min | Idempotency & backfill over a date range |
| D | 5 min | Write a real **Airflow DAG**, parse it, run it with `airflow dags test` |

> The notebook runs in plain Python for parts A–C. Part D has an optional install cell for Airflow (needs a few minutes; may be pre-installed by the instructor).

---

## 6. Wrap-up (5 min)

### Key takeaways
1. Orchestrate = **dependencies + state + retries + history + backfill**.
2. Everything hinges on **idempotent, parametrized, atomic** tasks.
3. Airflow = scheduler + executor + metadata DB + workers; DAGs are Python code.
4. Orchestrators **coordinate**; Spark/dbt/warehouses **compute**.
5. Tool choice depends on paradigm (task vs. asset vs. event) and team context.

### Quick quiz
1. Why is `INSERT INTO t SELECT ... WHERE day = CURRENT_DATE` a bad idea in a retried task?
2. What's the difference between the scheduler and the executor in Airflow?
3. Why should you not pass a 2 GB DataFrame through XCom? What do you pass instead?
4. A daily DAG with logical date 2025-03-10: which data does it process and when does it start?
5. When would Dagster be a better fit than Airflow?

<details>
<summary>Answers</summary>

1. Not idempotent: every retry/rerun duplicates rows, and it depends on wall-clock time so backfills are wrong. Use `{{ ds }}` and delete-then-insert / MERGE / partition overwrite.
2. The scheduler decides *what* and *when* to run (creates runs, queues ready tasks); the executor decides *how/where* queued tasks are executed (local process, Celery workers, Kubernetes pods).
3. XCom is stored in the metadata DB and is meant for small metadata. Write data to object storage/warehouse and pass the URI/table name.
4. It processes 2025-03-10 00:00 → 2025-03-11 00:00 and starts shortly after 2025-03-11 00:00 (after the interval closes).
5. When the focus is on data assets, lineage, partitions, data-quality checks and local testability (e.g. dbt-centered analytics platforms).
</details>

### Take-home assignment (optional, ≈ 2h)
Build a DAG `weather_pipeline` that:
1. Fetches the list of 5 cities (task 1) and **maps** one extraction task per city from a public API (e.g. Open-Meteo).
2. Writes each result to `data/{{ ds }}/{city}.json` (**idempotent** overwrite).
3. Aggregates the files and writes `data/{{ ds }}/summary.csv`.
4. Has `retries=3` with exponential backoff and a `trigger_rule="all_done"` notification task.
5. Is validated by a **pytest `DagBag` test** (no import errors, no cycles, expected task count).
6. *Bonus:* re-implement the same pipeline in Prefect **or** Dagster and write a 1-page comparison.

---

## References & further reading

- Apache Airflow documentation – <https://airflow.apache.org/docs/>
- Airflow best practices – <https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html>
- Airflow 3 upgrade guide – <https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading_to_airflow3.html>
- Prefect docs – <https://docs.prefect.io>
- Dagster docs – <https://docs.dagster.io>
- Harenslak & de Ruiter, *Data Pipelines with Apache Airflow* (Manning)
- Reis & Housley, *Fundamentals of Data Engineering* (O'Reilly) – chapter on orchestration
- Python `graphlib` – <https://docs.python.org/3/library/graphlib.html>
