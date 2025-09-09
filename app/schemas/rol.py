from pydantic import BaseModel
from typing import Optional

class RolCreate(BaseModel):
    name:str
    description: str | None = None

class RolOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True

class RolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
