from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, text
from app.models.orden import Orden, OrdenDetalle
from app.models.producto_variante import Producto_Variante
from app.models.sucursal import Sucursal
from datetime import datetime
from zoneinfo import ZoneInfo

ECUADOR_TZ = ZoneInfo("America/Guayaquil")

def reporte_ventas(id_sucursal: str, fecha_inicio: datetime, fecha_fin: datetime, db: Session):
    # Filtrar por la fecha de Ecuador en la DB
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
            Orden.estado != 'Anulado',  # <-- Excluir órdenes anuladas
            func.date(
                text("(ordenes.fecha AT TIME ZONE 'UTC' AT TIME ZONE 'America/Guayaquil')")
            ) >= fecha_inicio.date(),
            func.date(
                text("(ordenes.fecha AT TIME ZONE 'UTC' AT TIME ZONE 'America/Guayaquil')")
            ) <= fecha_fin.date()
        )
        .order_by(Orden.fecha.desc())
    )

    result = db.execute(query)
    ordenes = result.scalars().all()

    total_ventas = sum(
        sum(detalle.subtotal for detalle in orden.detalles_orden)
        for orden in ordenes
    )

    total_cantidad_productos = sum(
        sum(detalle.cantidad for detalle in orden.detalles_orden)
        for orden in ordenes
    )

    # Convertir cada fecha a hora de Ecuador para mostrar
    for orden in ordenes:
        if orden.fecha:
            orden.fecha = orden.fecha.replace(tzinfo=ZoneInfo("UTC")).astimezone(ECUADOR_TZ)

    return {
        "sucursal_id": id_sucursal,
        "sucursal_nombre": ordenes[0].sucursal.nombre if ordenes else None,
        "local_nombre": ordenes[0].sucursal.local.name if ordenes and ordenes[0].sucursal.local else None,
        "fecha_inicio": fecha_inicio.date(),
        "fecha_fin": fecha_fin.date(),
        "total_ventas": total_ventas,
        "total_cantidad_productos": total_cantidad_productos,
        "ordenes": [
            {
                "id": orden.id,
                "numero_orden": orden.numero_orden,
                "fecha": orden.fecha.strftime("%Y-%m-%d %H:%M:%S"),
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