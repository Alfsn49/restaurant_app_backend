from pydantic import BaseModel
from typing import Optional
from app.schemas.local import LocalOut

class SucursalCreate(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    ruc: str
    local_id: str


class SucursalOutSimple(BaseModel):
    id: str
    nombre: str
    direccion: str
    ruc: str
    telefono: str
    is_active: bool
    local_id: str

    class Config:
        from_attributes = True

class SucursalOut(BaseModel):
    id: str
    nombre: str
    direccion: str
    telefono: str
    ruc: str
    telefono: str
    is_active: bool
    local_id: str
    local: Optional[LocalOut]

    class Config:
        from_attributes = True

class SucursalUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    ruc: Optional[str] = None
    local_id: Optional[str] = None

    class Config:
        from_attributes = True

