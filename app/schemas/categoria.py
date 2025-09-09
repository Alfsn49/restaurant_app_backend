from pydantic import BaseModel
from typing import List, Optional

class CategoriaCreate(BaseModel):
    name: str

class CategoriaOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # ← en lugar de orm_mode (Pydantic v2)

class CategoriaUpdate(BaseModel):
    name: Optional[str]