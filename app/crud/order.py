from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models.orden import Orden, OrdenDetalle
from app.models.producto_variante import Producto_Variante
from app.models.sucursal import Sucursal
from app.models.inventario import Inventario

from datetime import datetime

async def crear_orden(db: AsyncSession, orden_data: dict, imprimir_local=True):
    sucursal_id = orden_data["sucursal_id"]

    # 1️⃣ Obtener último número de orden
    result = await db.execute(
        select(Orden)
        .where(Orden.sucursal_id == sucursal_id)
        .order_by(desc(Orden.numero_orden))
    )
    last_order = result.scalars().first()
    next_order_number = 1 if not last_order else last_order.numero_orden + 1

    # 2️⃣ Crear orden
    orden = Orden(numero_orden=next_order_number, sucursal_id=sucursal_id)
    db.add(orden)
    await db.flush()

    # 3️⃣ Crear detalles y actualizar inventario
    for item in orden_data["items"]:
        detalle = OrdenDetalle(
            orden_id=orden.id,
            producto_variante_id=item["product_variante_id"],
            cantidad=item["cantidad"],
            precio_unitario=item["precio"],
            subtotal=item["cantidad"] * item["precio"]
        )
        db.add(detalle)

        # 🔹 Reducir inventario
        result_inv = await db.execute(
            select(Inventario)
            .where(
                Inventario.producto_variante_id == item["product_variante_id"],
                Inventario.sucursal_id == sucursal_id
            )
        )
        inventario = result_inv.scalars().first()

        if not inventario:
            raise ValueError(f"No hay inventario registrado para la variante {item['product_variante_id']} en la sucursal {sucursal_id}")

        if inventario.cantidad < item["cantidad"]:
            raise ValueError(
                f"No hay suficiente stock de la variante {item['product_variante_id']}. Disponible: {inventario.cantidad}, pedido: {item['cantidad']}"
            )

        inventario.cantidad -= item["cantidad"]
        db.add(inventario)

    await db.commit()
    await db.refresh(orden)

    # 4️⃣ Cargar sucursal y local
    result = await db.execute(
        select(Orden)
        .options(selectinload(Orden.sucursal).selectinload(Sucursal.local))
        .where(Orden.id == orden.id)
    )
    orden = result.scalars().first()

    # 5️⃣ Consultar detalles con productos y zonas
    result = await db.execute(
        select(OrdenDetalle)
        .options(
            selectinload(OrdenDetalle.producto_variantes)
            .selectinload(Producto_Variante.producto),
            selectinload(OrdenDetalle.producto_variantes)
            .selectinload(Producto_Variante.zona)
        )
        .where(OrdenDetalle.orden_id == orden.id)
    )
    detalles = result.scalars().all()

    # 6️⃣ Agrupar por zona
    tickets_por_zona = {}
    for detalle in detalles:
        variante = detalle.producto_variantes
        producto = variante.producto
        zona = variante.zona
        nombre_completo = f"{producto.nombre} - {variante.nombre}" if producto else variante.nombre
        zona_nombre = zona.name if zona else "Sin zona"
        tickets_por_zona.setdefault(zona_nombre, []).append({
            "producto": nombre_completo,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal
        })

    # 7️⃣ Generar "texto del ticket" en lugar de escribir en la impresora
    sucursal_nombre = orden.sucursal.nombre if orden.sucursal else "SUCURSAL"
    local_nombre = orden.sucursal.local.name if orden.sucursal and orden.sucursal.local else "LOCAL"

    ticket_lines = []
    ticket_lines.append(sucursal_nombre)
    ticket_lines.append(local_nombre)
    ticket_lines.append(f"TICKET ORDEN #{orden.numero_orden}")
    ticket_lines.append("="*32)

    total_general = 0
    for zona_nombre, items in tickets_por_zona.items():
        ticket_lines.append(f"*** Zona: {zona_nombre} ***")
        subtotal_zona = 0
        for item in items:
            nombre = item['producto'][:25].ljust(25)
            cantidad = str(item['cantidad']).rjust(2)
            precio = f"{item['precio_unitario']:.2f}".rjust(6)
            ticket_lines.append(f"{nombre} x{cantidad} ${precio}")
            subtotal_zona += item['subtotal']
        ticket_lines.append("-"*32)
        ticket_lines.append(f"Subtotal zona: ${subtotal_zona:.2f}")
        total_general += subtotal_zona

    ticket_lines.append("="*32)
    ticket_lines.append(f"TOTAL: ${total_general:.2f}")
    ticket_lines.append("="*32)
    ticket_lines.append("¡Gracias por su pedido!")
    ticket_lines.append("\n"*3)  # Saltos extra

    ticket_text = "\n".join(ticket_lines)

    # 8️⃣ Respuesta al frontend
    return {
        "message": "Orden creada con éxito",
        "orden_id": orden.id,
        "tickets_por_zona": tickets_por_zona,
        "ticket_text": ticket_text   # 👈 aquí va el texto completo como lo ibas a imprimir
    }



async def list_ordenes(id_sucursal:str, fecha_inicio: datetime, fecha_fin: datetime, db: AsyncSession):

    result = await db.execute(select(Orden).options(selectinload(Orden.detalles_orden)).where(Orden.sucursal_id == id_sucursal, 
    func.date(Orden.fecha) >= fecha_inicio.date(), func.date(Orden.fecha) <= fecha_fin.date()).order_by((Orden.fecha.desc())))

    return result.scalars().all()