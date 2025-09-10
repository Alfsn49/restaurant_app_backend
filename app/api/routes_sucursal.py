from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, get_db
from app.schemas.sucursal import SucursalCreate, SucursalUpdate, SucursalOut, SucursalOutSimple
from app.crud.sucursal import create_sucursal, get_sucursales, get_sucursal_by_id, update_sucursal, get_sucursal_by_name, soft_delete_sucursal, get_sucursal_by_id_local
from app.utils.auth import role_required

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.get("/get-sucursales", response_model=list[SucursalOut])
def list_sucursales(db: Session = Depends(get_db)):
    return get_sucursales(db)


@router.get("/get-sucursal/{id_local}", response_model=list[SucursalOutSimple])
def list_sucursal_by_id_local(id_local: str, db: Session = Depends(get_db)):
    return get_sucursal_by_id_local(id_local, db)


@router.post("/create-sucursal", response_model=SucursalOutSimple, status_code=status.HTTP_201_CREATED)
def create_new_sucursal(sucursal: SucursalCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si ya existe una sucursal con ese nombre
        existing_sucursal = get_sucursal_by_name(db, sucursal.nombre)
        if existing_sucursal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una sucursal con este nombre"
            )

        sucursal = create_sucursal(
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
def update_sucursal_route(
    sucursal_id: str,
    sucursal_data: SucursalUpdate,
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)
):
    sucursal = update_sucursal(db, sucursal_id, sucursal_data)
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    return {
        "message": "Sucursal actualizada exitosamente"
    }


@router.delete("/delete/{sucursal_id}")
def soft_delete_sucursal_route(
    sucursal_id: str,
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)
):
    sucursal = soft_delete_sucursal(db, sucursal_id)

    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    return {
        "message": "Sucursal eliminada exitosamente"
    }
