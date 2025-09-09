from pydantic import BaseModel
from typing import List

class OrdenDetalleCreate(BaseModel):
    product_variante_id: int
    cantidad: int
    precio: float

class OrdenCreate(BaseModel):
    sucursal_id: str
    items: List[OrdenDetalleCreate]
