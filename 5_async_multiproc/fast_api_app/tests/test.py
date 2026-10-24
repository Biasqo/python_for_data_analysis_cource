import requests

BASE = "http://127.0.0.1:8000"


def show(label, r):
    print(f"\n--- {label} ---")
    print("status:", r.status_code)
    try:
        print("json:", r.json())
    except Exception:
        print("text:", r.text)


if __name__ == "__main__":
    show("GET /", requests.get(f"{BASE}/"))
    show("GET /health", requests.get(f"{BASE}/health"))
    show("GET /items", requests.get(f"{BASE}/items"))
    show("GET /items?limit=1",
         requests.get(f"{BASE}/items", params={"limit": 1}))
    show("GET /items?name_contains=ban",
         requests.get(f"{BASE}/items", params={"name_contains": "ban"}))
    show("GET /items/1", requests.get(f"{BASE}/items/1"))
    show("GET /items/999 (404)", requests.get(f"{BASE}/items/999"))

    r = requests.post(f"{BASE}/items", json={"name": "cherry", "price": 3.25})
    show("POST /items", r)
    new_id = r.json()["id"]

    show("PUT /items (price only)",
         requests.put(f"{BASE}/items/{new_id}", json={"price": 4.00}))

    show("POST /echo", requests.post(f"{BASE}/echo",
                                     params={"text": "hi", "times": 3}))

    show(f"DELETE /items/{new_id}",
         requests.delete(f"{BASE}/items/{new_id}"))
    show(f"GET /items/{new_id} (should be 404)",
         requests.get(f"{BASE}/items/{new_id}"))

    show("POST /items invalid",
         requests.post(f"{BASE}/items", json={"name": "x", "price": "abc"}))
