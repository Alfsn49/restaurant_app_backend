from sqlalchemy.orm import Session, selectinload  # Cambiado de 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.rol import RolCreate, RolUpdate, RolOut
from app.crud.rol import create_rol, get_rols, get_rol_by_id, update_rol, get_rol_by_name


router = APIRouter(prefix="/rols", tags=["Roles"])



@router.get("/get-rols", response_model=list[RolOut])
def list_rols(db: Session = Depends(get_db)):
    roles =  get_rols(db)
    for rol in roles:
        print(RolOut.model_validate(rol).model_dump())
    return get_rols(db)

@router.post("/create-rol", response_model=RolOut, status_code=status.HTTP_201_CREATED)
def create_new_rol(rol: RolCreate, db: Session = Depends(get_db)):
    existing_rol =  get_rol_by_name(db, rol.name)
    print("Ver rol", existing_rol)
    if existing_rol:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="El rol ya existe")
    return create_rol(db, rol.name, rol.description)