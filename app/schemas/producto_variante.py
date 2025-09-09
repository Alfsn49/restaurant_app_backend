from pydantic import BaseModel
from typing import List, Optional

class Producto_Variante_Create(BaseModel):
    nombre: str
    precio: float
    producto_id: str
    menu_id: int
    zona_id: int
    cantidad: int



class Producto_Variante_Out(BaseModel):
    id:int
    nombre: str
    precio: float
    disponible: bool
    producto_id: str
    menu_id: int
    zona_id: int

    class Config:
        from_attributes = True 

class Producto_Variante_Update(BaseModel):
    nombre: Optional[str]
    precio: Optional[float]
    disponible: Optional[bool]
    producto_id: Optional[str]
    menu_id: Optional[int]
    zona_id: Optional[int]
    cantidad: Optional[int]  # <-- para stock / inventario