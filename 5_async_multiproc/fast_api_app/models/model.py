from pydantic import BaseModel, Field
from typing import Optional


class Item(BaseModel):
    name: str = Field(..., min_length=1, examples=["apple"])
    price: float = Field(..., ge=0, examples=[1.5])


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, ge=0)


class ItemOut(BaseModel):
    id: int
    name: str
    price: float
