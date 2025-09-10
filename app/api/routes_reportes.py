from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import datetime
from app.crud.reports import reporte_ventas

router = APIRouter(prefix="/reportes", tags=["reportes"])

@router.get("/reporte-ventas")
def get_reporte_ventas(
    id_sucursal: str,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    db: Session = Depends(get_db)
):
    return reporte_ventas(id_sucursal, fecha_inicio, fecha_fin, db)
