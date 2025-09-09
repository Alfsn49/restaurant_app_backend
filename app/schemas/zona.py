from pydantic import BaseModel
from typing import Optional, List

class ZonaCreate(BaseModel):
    name: str
    sucursal_id: str

class ZonaOut(BaseModel):
    id: int
    name: str
    sucursal_id: str

    class Config:
        from_attributes = True

class ZonaUpdate(BaseModel):
    name: Optional[str] = None