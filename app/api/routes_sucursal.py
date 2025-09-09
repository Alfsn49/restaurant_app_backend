from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal, get_db
from app.schemas.sucursal import SucursalCreate, SucursalUpdate, SucursalOut,SucursalOutSimple
from app.crud.sucursal import create_sucursal, get_sucursales, get_sucursal_by_id, update_sucursal, get_sucursal_by_name, soft_delete_sucursal, get_sucursal_by_id_local
from app.utils.auth import  role_required

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])

@router.get("/get-sucursales", response_model=list[SucursalOut])
async def list_sucursales(db: AsyncSession = Depends(get_db)):
    return await get_sucursales(db)

@router.get("/get-sucursal/{id_local}", response_model=list[SucursalOutSimple])
async def list_sucursal_by_id_local(id_local:str ,db: AsyncSession = Depends(get_db)):
    return await get_sucursal_by_id_local(id_local, db)

@router.post("/create-sucursal", response_model=SucursalOutSimple, status_code=status.HTTP_201_CREATED)
async def create_new_sucursal(
    sucursal: SucursalCreate,
    db: AsyncSession = Depends(get_db)
):
    try:        
        # Verificar si ya existe una sucursal con ese nombre
        existing_sucursal = await get_sucursal_by_name(db, sucursal.nombre)
        if existing_sucursal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una sucursal con este nombre"
            )

        sucursal = await create_sucursal(
            db=db,
            nombre=sucursal.nombre,
            direccion=sucursal.direccion,
            ruc=sucursal.ruc,
            telefono=sucursal.telefono,
            local_id=sucursal.local_id
        )
        return sucursal

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sucursal: {str(e)}"
        )

@router.patch("/update/{sucursal_id}")
async def update_sucursal_route(sucursal_id: str, sucursal_data: SucursalUpdate, current_user: dict = Depends(role_required("Administrador", "Dueño")), db: AsyncSession = Depends(get_db)):
    sucursal = await update_sucursal(db, sucursal_id, sucursal_data)
    if not sucursal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sucursal no encontrada")
    
    return{
        "message": "Sucursal actualizada exitosamente"
    }

@router.delete("/delete/{sucursal_id}")
async def soft_delete_sucursal_route(sucursal_id: str, current_user:
    dict = Depends(role_required("Administrador", "Dueño")), db: AsyncSession = Depends(get_db)):
    sucursal = await soft_delete_sucursal(db, sucursal_id)

    if not sucursal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sucursal no encontrada")
    
    return {
        "message" : "Sucursal eliminada exitosamente"
    }