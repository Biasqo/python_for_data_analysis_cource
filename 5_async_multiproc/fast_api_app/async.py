import asyncio
import httpx
import time

BASE = "http://127.0.0.1:8000"


async def one_call(client: httpx.AsyncClient):
    r = await client.get("/items/1")
    return r.status_code, r.json()


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=10) as client:
        r = await client.get("/")
        print("GET /:", r.status_code, r.json())

        r = await client.post("/items", json={"name": "kiwi", "price": 2.2})
        print("POST /items:", r.status_code, r.json())
        new_id = r.json()["id"]

        urls = [f"/items/{i}" for i in range(1, 6)]
        results = await asyncio.gather(*(client.get(u) for u in urls))
        for u, r in zip(urls, results):
            print(u, "->", r.status_code, r.json())

        sem = asyncio.Semaphore(10)
        async def bounded_get(i: int):
            async with sem:
                r = await client.get(f"/items/{i}")
                return i, r.status_code

        out = await asyncio.gather(*(bounded_get(i) for i in range(1, 50)))
        print("bounded:", out[:5], "...")

        r = await client.get("/items/9999")
        print("404 case:", r.status_code, r.json())

        await client.delete(f"/items/{new_id}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"{time.time() - start_time:.2f} сек")
