from pydantic import BaseModel
from typing import List, Optional
from app.schemas.sucursal import SucursalOut, SucursalOutSimple

class MenuCreate(BaseModel):
    name: str
    horario: str
    sucursal_id: str

class MenuOutSimple(BaseModel):
    id: int
    name: str
    horario: str
    sucursal_id: str

    class Config:
        from_attributes = True

class MenuOut(BaseModel):
    id: int
    name: str
    horario: str
    sucursal_id: str
    sucursal: Optional[SucursalOut]

    class Config:
        from_attributes = True  # Pydantic v2 uses from_attributes instead of orm_mode

class MenuUpdate(BaseModel):
    name: Optional[str] = None
    horario: Optional[str] = None
    sucursal_id: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2 uses from_attributes instead of orm_mode