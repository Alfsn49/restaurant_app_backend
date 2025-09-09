from pydantic import BaseModel
from typing import Optional, List


class LocalCreate(BaseModel):
    name: str
    direccion: str
    telefono: Optional[str] = None

    ruc: str


class LocalOut(BaseModel):
    id: str
    name: str
    direccion: str
    telefono: str | None = None
    ruc:str
    is_active: bool

    class Config:
        from_attributes = True

class LocalUpdate(BaseModel):
    name: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    ruc: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True