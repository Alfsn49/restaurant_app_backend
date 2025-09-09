from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models.orden import Orden, OrdenDetalle
from app.models.producto_variante import Producto_Variante
from app.models.product import Product
from app.models.sucursal import Sucursal

from datetime import datetime


async def reporte_ventas(id_sucursal: str, fecha_inicio: datetime, fecha_fin: datetime, db: AsyncSession):
    query = (
        select(Orden)
        .options(
            selectinload(Orden.detalles_orden)
            .selectinload(OrdenDetalle.producto_variantes)
            .selectinload(Producto_Variante.producto),
            selectinload(Orden.sucursal).selectinload(Sucursal.local)
        )
        .where(
            Orden.sucursal_id == id_sucursal,
            func.date(Orden.fecha) >= fecha_inicio.date(),
            func.date(Orden.fecha) <= fecha_fin.date()
        )
        .order_by(Orden.fecha.desc())
    )

    result = await db.execute(query)
    ordenes = result.scalars().all()

    total_ventas = sum(
        sum(detalle.subtotal for detalle in orden.detalles_orden) 
        for orden in ordenes
    )

    return {
        "sucursal_id": id_sucursal,
        "sucursal_nombre": ordenes[0].sucursal.nombre if ordenes else None,
        "local_nombre": ordenes[0].sucursal.local.name if ordenes and ordenes[0].sucursal.local else None,
        "fecha_inicio": fecha_inicio.date(),
        "fecha_fin": fecha_fin.date(),
        "total_ventas": total_ventas,
        "ordenes": [
            {
                "id": orden.id,
                "numero_orden": orden.numero_orden,
                "fecha": orden.fecha,
                "detalles": [
                    {
                        "producto": f"{d.producto_variantes.producto.nombre} - {d.producto_variantes.nombre}",
                        "cantidad": d.cantidad,
                        "precio_unitario": d.precio_unitario,
                        "subtotal": d.subtotal
                    }
                    for d in orden.detalles_orden
                ]
            }
            for orden in ordenes
        ]
    }
