from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from datetime import datetime
from app.crud.reports import reporte_ventas

router = APIRouter(prefix="/reportes", tags=["reportes"])

@router.get("/reporte-ventas")
async def get_reporte_ventas(
    id_sucursal: str,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    db: AsyncSession = Depends(get_db)
):
    return await reporte_ventas(id_sucursal, fecha_inicio, fecha_fin, db)
