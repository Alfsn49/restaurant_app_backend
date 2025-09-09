from pydantic import BaseModel
from typing import List, Optional
from app.schemas.categoria import CategoriaOut
from app.schemas.producto_variante import Producto_Variante_Out
class ProductoCreate(BaseModel):
    nombre:str
    categoria_id:int
    sucursal_id:str

class ProductoOut(BaseModel):
    id:str
    nombre:str
    disponible:bool
    categoria_id:int
  

    class Config:
        from_attributes = True  # Pydantic v2 uses from_attributes instead of orm_mode

class ProductOutDetail(ProductoOut):
    categoria:Optional[CategoriaOut]
    variantes:List[Producto_Variante_Out] = []

class ProductoUpdate(BaseModel):
    nombre: Optional[str]
    disponible: Optional[bool]
    categoria_id: Optional[int]
    sucursal_id:str
