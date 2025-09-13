from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models.orden import Orden, OrdenDetalle
from app.models.producto_variante import Producto_Variante
from app.models.sucursal import Sucursal
from app.models.inventario import Inventario

from datetime import datetime

def crear_orden(db: Session, orden_data: dict, imprimir_local=True):
    sucursal_id = orden_data["sucursal_id"]

    # 1️⃣ Obtener último número de orden
    result = db.execute(
        select(Orden)
        .where(Orden.sucursal_id == sucursal_id)
        .order_by(desc(Orden.numero_orden))
    )
    last_order = result.scalars().first()
    next_order_number = 1 if not last_order else last_order.numero_orden + 1

    # 2️⃣ Crear orden
    orden = Orden(numero_orden=next_order_number, sucursal_id=sucursal_id, estado="Pagado")
    db.add(orden)
    db.flush()

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

        # Reducir inventario
        result_inv = db.execute(
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
            raise ValueError(f"No hay suficiente stock de la variante {item['product_variante_id']}. Disponible: {inventario.cantidad}, pedido: {item['cantidad']}")
        inventario.cantidad -= item["cantidad"]
        db.add(inventario)

    db.commit()
    db.refresh(orden)

    # 4️⃣ Cargar sucursal y local
    result = db.execute(
        select(Orden)
        .options(selectinload(Orden.sucursal).selectinload(Sucursal.local))
        .where(Orden.id == orden.id)
    )
    orden = result.scalars().first()

    # 5️⃣ Consultar detalles con productos y zonas
    result = db.execute(
        select(OrdenDetalle)
        .options(
            selectinload(OrdenDetalle.producto_variantes).selectinload(Producto_Variante.producto),
            selectinload(OrdenDetalle.producto_variantes).selectinload(Producto_Variante.zona)
        )
        .where(OrdenDetalle.orden_id == orden.id)
    )
    detalles = result.scalars().all()

    # 6️⃣ Agrupar por zona
    tickets_por_zona = {}
    total_general = 0
    for detalle in detalles:
        variante = detalle.producto_variantes
        producto = variante.producto
        zona = variante.zona
        nombre_completo = f"{variante.nombre}" if producto else variante.nombre
        zona_nombre = zona.name if zona else "Sin zona"
        tickets_por_zona.setdefault(zona_nombre, []).append({
            "producto": nombre_completo,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal
        })
        total_general += detalle.subtotal

    sucursal_nombre = orden.sucursal.nombre if orden.sucursal else "SUCURSAL"
    local_nombre = orden.sucursal.local.name if orden.sucursal and orden.sucursal.local else "LOCAL"

    # 7️⃣ Crear tickets separados (uno por zona, el último incluye total)
    tickets_array = []
    num_zonas = len(tickets_por_zona)

    for idx, (zona_nombre, items) in enumerate(tickets_por_zona.items(), 1):
        lines = []

        # Encabezado solo en la primera zona
        if idx == 1:
            lines.append(sucursal_nombre)
            lines.append(local_nombre)
            lines.append(f"TICKET ORDEN #{orden.numero_orden}")
            lines.append("="*32)

        # Zona
        lines.append(f"*** Zona: {zona_nombre} ***")
        subtotal_zona = 0
        for item in items:
            nombre = item['producto'][:25].ljust(25)
            cantidad = str(item['cantidad']).rjust(2)
            precio = f"{item['precio_unitario']:.2f}".rjust(6)
            lines.append(f"{nombre} Cant: {cantidad} ${precio}")
            subtotal_zona += item['subtotal']

        lines.append("-"*32)
        lines.append(f"Subtotal zona: ${subtotal_zona:.2f}")

        # Última zona agrega total general y mensaje
        if idx == num_zonas:
            lines.append("="*32)
            lines.append(f"TOTAL: ${total_general:.2f}")
            lines.append("="*32)
            lines.append("¡Gracias por su pedido!")

        # Unir líneas usando CRLF para compatibilidad Linux/Windows
        ticket_text = "\r\n".join(lines)
        tickets_array.append(ticket_text)

    return {
        "message": "Orden creada con éxito",
        "orden_id": orden.id,
        "tickets_por_zona": tickets_por_zona,
        "tickets_array": tickets_array  # ✅ cada ticket separado
    }

def list_ordenes(id_sucursal:str, fecha_inicio: datetime, fecha_fin: datetime, db: Session):

    result =  db.execute(select(Orden).options(selectinload(Orden.detalles_orden)).where(Orden.sucursal_id == id_sucursal, 
    func.date(Orden.fecha) >= fecha_inicio.date(), func.date(Orden.fecha) <= fecha_fin.date()).order_by((Orden.fecha.desc())))

    return result.scalars().all()


def cancelar_orden(id_orden: str, db: Session):
    # 1️⃣ Buscar la orden
    result = db.execute(
        select(Orden)
        .options(selectinload(Orden.detalles_orden))  # cargamos también los detalles
        .where(Orden.id == id_orden)
    )
    orden = result.scalars().first()

    if not orden:
        raise ValueError(f"No existe una orden con id {id_orden}")

    # 2️⃣ Validar que no esté ya cancelada
    if orden.estado == "Anulado":
        raise ValueError(f"La orden {id_orden} ya está cancelada")

    # 3️⃣ Iterar por los detalles y devolver el stock
    for detalle in orden.detalles_orden:
        result_inv = db.execute(
            select(Inventario).where(
                Inventario.producto_variante_id == detalle.producto_variante_id,
                Inventario.sucursal_id == orden.sucursal_id
            )
        )
        inventario = result_inv.scalars().first()

        if inventario:
            inventario.cantidad += detalle.cantidad  # devolvemos stock
            db.add(inventario)

    # 4️⃣ Actualizar estado de la orden
    orden.estado = "Anulado"
    db.add(orden)

    # 5️⃣ Guardar cambios
    db.commit()
    db.refresh(orden)

    return {
        "message": f"Orden {orden.id} cancelada con éxito",
        "orden_id": orden.id,
        "estado": orden.estado
    }
