import asyncio
import httpx

BASE = "http://127.0.0.1:8000"


async def one_call(client: httpx.AsyncClient):
    r = await client.get("/items/1")
    return r.status_code, r.json()


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=10) as client:
        # 1. Simple awaited call
        r = await client.get("/")
        print("GET /:", r.status_code, r.json())

        # 2. POST with JSON
        r = await client.post("/items", json={"name": "kiwi", "price": 2.2})
        print("POST /items:", r.status_code, r.json())
        new_id = r.json()["id"]

        # 3. Fire many requests concurrently
        urls = [f"/items/{i}" for i in range(1, 6)]
        results = await asyncio.gather(*(client.get(u) for u in urls))
        for u, r in zip(urls, results):
            print(u, "->", r.status_code, r.json())

        # 4. Bounded concurrency with a semaphore (avoid hammering the server)
        sem = asyncio.Semaphore(10)

        async def bounded_get(i: int):
            async with sem:
                r = await client.get(f"/items/{i}")
                return i, r.status_code

        out = await asyncio.gather(*(bounded_get(i) for i in range(1, 50)))
        print("bounded:", out[:5], "...")

        # 5. Error handling — check status, don't assume 200
        r = await client.get("/items/9999")
        print("404 case:", r.status_code, r.json())

        # 6. Cleanup
        await client.delete(f"/items/{new_id}")


if __name__ == "__main__":
    asyncio.run(main())
