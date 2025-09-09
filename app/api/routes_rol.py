from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.rol import RolCreate, RolUpdate, RolOut
from app.crud.rol import create_rol, get_rols, get_rol_by_id, update_rol, get_rol_by_name


router = APIRouter(prefix="/rols", tags=["Roles"])



@router.get("/get-rols", response_model=list[RolOut])
async def list_rols(db: AsyncSession = Depends(get_db)):
    roles = await get_rols(db)
    for rol in roles:
        print(RolOut.model_validate(rol).model_dump())
    return await get_rols(db)

@router.post("/create-rol", response_model=RolOut, status_code=status.HTTP_201_CREATED)
async def create_new_rol(rol: RolCreate, db: AsyncSession = Depends(get_db)):
    existing_rol = await get_rol_by_name(db, rol.name)
    print("Ver rol", existing_rol)
    if existing_rol:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="El rol ya existe")
    return await create_rol(db, rol.name, rol.description)