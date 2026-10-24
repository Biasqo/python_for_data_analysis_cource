from typing import Dict, Optional
from models.model import Item


class InMemoryStore:
    def __init__(self) -> None:
        self._data: Dict[int, dict] = {}
        self._next_id: int = 1

    def create(self, item: Item) -> dict:
        item_id = self._next_id
        self._data[item_id] = item.model_dump()
        self._next_id += 1
        return {"id": item_id, **self._data[item_id]}

    def get(self, item_id: int) -> Optional[dict]:
        if item_id not in self._data:
            return None
        return {"id": item_id, **self._data[item_id]}

    def list(self, limit: int = 10, name_contains: Optional[str] = None) -> list[dict]:
        result = []
        for i, item in self._data.items():
            if name_contains and name_contains.lower() not in item["name"].lower():
                continue
            result.append({"id": i, **item})
        return result[:limit]

    def update(self, item_id: int, fields: dict) -> Optional[dict]:
        if item_id not in self._data:
            return None
        self._data[item_id].update(fields)
        return {"id": item_id, **self._data[item_id]}

    def delete(self, item_id: int) -> bool:
        return self._data.pop(item_id, None) is not None


store = InMemoryStore()
store.create(Item(name="apple", price=1.50))
store.create(Item(name="banana", price=0.50))
