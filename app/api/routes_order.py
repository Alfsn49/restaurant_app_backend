from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.order import OrdenCreate
from app.crud.order import crear_orden, list_ordenes, cancelar_orden
from app.utils.auth import role_required
from datetime import datetime

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])

@router.post("/create", response_model=dict)
def crear_orden_endpoint(orden: OrdenCreate, current_user: dict = Depends(role_required("Administrador", "Dueño")),db: Session = Depends(get_db)):
    print(orden)
    nueva_orden = crear_orden(db, orden.dict())
    return {
        "message": "Orden creada con éxito",
        "orden_id": nueva_orden["orden_id"],  # <- así accedes al id
        "tickets_por_zona": nueva_orden["tickets_por_zona"],
        "ticket_text":nueva_orden["ticket_text"]
    }


@router.get("/list")
def listar_ordenes_endpoint(id_sucursal:str,
    fecha_inicio: datetime,
    fecha_fin: datetime, current_user: dict = Depends(role_required("Administrador", "Dueño")),db: Session = Depends(get_db)):
    print('Fecha de inicio', fecha_inicio)
    print('Fecha de fin', fecha_fin)
    ordenes = list_ordenes(id_sucursal, fecha_inicio, fecha_fin, db)

    return ordenes


@router.get("/cancelar/{id_orden}")
def cancelar_ordenes_endpoint(id_orden:str, current_user: dict = Depends(role_required("Administrador", "Dueño")), db: Session = Depends(get_db)):
    orden =  cancelar_orden(id_orden, db)
    return orden