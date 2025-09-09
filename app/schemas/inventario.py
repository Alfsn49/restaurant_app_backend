from pydantic import BaseModel
from typing import Optional

class InventarioCreate(BaseModel):
    cantidad: int
    producto_variante_id:int
    sucursal_id:int

class InventarioOut(BaseModel):
    id: int
    cantidad: int
    producto_variante_id:int
    sucursal_id:int

    class Config:
        from_attributes = True

class InventarioUpdate(BaseModel):
    cantidad: Optional[int]
    producto_variante_id: Optional[int]
    sucursal_id: Optional[int]
    