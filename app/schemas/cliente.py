from pydantic import BaseModel
from typing import List, Optional

class ClienteCreate(BaseModel):
    nombre: str
    ruc_cedula: str
    direccion: str
    telefono: str
    email: str

    sucursal_id: str


class ClienteOut(BaseModel):
    id: str
    nombre: str
    ruc_cedula: str
    direccion: str
    telefono: str
    email: str

    class Config:
        from_attributes = True

class ClienteUpdate(BaseModel):
    nombre: Optional[str]
    ruc_cedula: Optional[str]
    direccion: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    sucursal_id:Optional[str]
    