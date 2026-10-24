from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models.model import Item, ItemUpdate, ItemOut
from storage import store

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(
    limit: int = Query(10, ge=1, le=100),
    name_contains: Optional[str] = None,
):
    return store.list(limit=limit, name_contains=name_contains)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    item = store.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemOut, status_code=201)
def create_item(item: Item):
    return store.create(item)


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, item: ItemUpdate):
    fields = {k: v for k, v in item.model_dump().items() if v is not None}
    updated = store.update(item_id, fields)
    if updated is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete("/{item_id}")
def delete_item(item_id: int):
    if not store.delete(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": item_id}
