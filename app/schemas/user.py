from pydantic import BaseModel
from typing import List, Optional
from app.schemas.sucursal import SucursalOut
from app.schemas.rol import RolOut


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    name: str
    last_name: str
    rol_id: int  # Asumiendo que el rol es un ID entero
    sucursal_id:str

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]
    name: Optional[str]
    last_name: Optional[str]
    rol_id: Optional[int]
    sucursal_id: Optional[str]


class UserOut (BaseModel):
    id: str
    username: str
    email: str | None = None
    name: str
    last_name: str
    sucursal_id: str
    sucursal: Optional[SucursalOut]
    is_active: bool = True
    rol_id: int
    rol: Optional[RolOut]

    class Config:
        from_attributes = True  # ← en lugar de orm_mode (Pydantic v2)

class UserLogin(BaseModel):
    username: str
    password: str 