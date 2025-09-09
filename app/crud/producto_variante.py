from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.utils.sdkImage import upload_image_from_bytes, delete_image_by_url
from app.models.product import Product
from app.models.sucursal import Sucursal
from app.models.inventario import Inventario
from app.models.menu import Menu
from app.models.producto_variante import Producto_Variante
from app.schemas.producto_variante import Producto_Variante_Create, Producto_Variante_Update, Producto_Variante_Out


async def create_producto_variante(db: AsyncSession, nombre:str, precio:float, producto_id:str, menu_id:int, zona_id:int, cantidad:int ,image_file = None):
    # Obtener la sucursal asociada al menu
    stmt_sucursal = (
        select(Menu.sucursal_id)
        .where(Menu.id == menu_id)
    )
    result = await db.execute(stmt_sucursal)
    sucursal_id = result.scalars().first()

    if not sucursal_id:
        return None  # Menu no existe

    # Verificar si ya existe el producto en la misma sucursal
    stmt = (
        select(Producto_Variante)
        .join(Menu)
        .where(
            Producto_Variante.nombre == nombre,
            Menu.sucursal_id == sucursal_id
        )
    )
    result = await db.execute(stmt)
    existe = result.scalars().first()

    image_url = None

    if existe:
        return None

    if image_file:
        try:
            image_url = upload_image_from_bytes(
                file_bytes=image_file,
                public_id=f"variante_{nombre}",
                folder="variantes"

            )
        except Exception as e:
            raise RuntimeError(f"Error uploading image: {str(e)}")


    # Crear el producto variante
    nuevo_producto = Producto_Variante(
        nombre=nombre,
        precio=precio,
        producto_id=producto_id,
        menu_id=menu_id,
        zona_id=zona_id,
        image = image_url
    )
    db.add(nuevo_producto)
    await db.flush()

    # Crear inventario
    nuevo_inventario = Inventario(
        producto_variante_id=nuevo_producto.id,
        cantidad=cantidad,
        sucursal_id=sucursal_id
    )
    db.add(nuevo_inventario)

    await db.commit()
    await db.refresh(nuevo_producto)
    return nuevo_producto


async def list_productos_variantes(db:AsyncSession):
    result = await db.execute(select(Producto_Variante))
    return result.scalars().all()

async def specific_producto_variante(db:AsyncSession, id:int):
    result = await db.execute(select(Producto_Variante).where(Producto_Variante.id == id))
    return result.scalars().one_or_none()

async def update_variante(
    db: AsyncSession, 
    producto_variante_id: int, 
    nombre: str, 
    precio: float, 
    producto_id: str, 
    menu_id: int, 
    disponible: bool,
    zona_id: int, 
    cantidad: int,
    image_file=None, 
    image_url=None
):
    # 1. Buscar la variante a actualizar
    result = await db.execute(
        select(Producto_Variante).where(Producto_Variante.id == producto_variante_id)
    )
    producto_variante = result.scalars().first()

    if not producto_variante:
        return None

    # 2. Validar duplicados en el mismo menú
    query = await db.execute(
        select(Producto_Variante)
        .where(Producto_Variante.nombre == nombre)
        .where(Producto_Variante.menu_id == menu_id)
        .where(Producto_Variante.id != producto_variante_id)
    )
    existing = query.scalars().first()
    if existing:
        return "duplicado"

    # 3. Manejo de imagen
    new_image_url = None
    if image_file:
        try:
            # 🔥 Eliminar la imagen anterior si existe
            if producto_variante.image:
                try:
                    delete_image_by_url(producto_variante.image)
                except Exception as e:
                    print(f"⚠️ No se pudo borrar la imagen anterior: {str(e)}")

            # ✅ Subir nueva imagen con public_id único
            new_image_url = upload_image_from_bytes(
                file_bytes=image_file,
                public_id=f"variante_{producto_variante_id}_{nombre}",
                folder="variantes"
            )
        except Exception as e:
            raise RuntimeError(f"Error uploading image: {str(e)}")
    elif image_url:
        new_image_url = image_url

    # 4. Actualizar campos
    producto_variante.nombre = nombre
    producto_variante.precio = precio
    producto_variante.producto_id = producto_id
    producto_variante.menu_id = menu_id
    producto_variante.disponible = disponible
    producto_variante.zona_id = zona_id

    # 5. Actualizar inventario (cantidad)
    inventario_q = await db.execute(
        select(Inventario).where(Inventario.producto_variante_id == producto_variante_id)
    )
    inventario = inventario_q.scalars().first()

    if inventario:
        inventario.cantidad = cantidad
    else:
        nuevo_inventario = Inventario(
            producto_variante_id=producto_variante_id,
            sucursal_id=producto_variante.menu.sucursal_id,
            cantidad=cantidad
        )
        db.add(nuevo_inventario)

    # 6. Guardar la nueva imagen si hay
    if new_image_url:
        producto_variante.image = new_image_url

    # 7. Guardar cambios
    await db.commit()
    await db.refresh(producto_variante)

    return producto_variante



async def delete_soft_producto(db:AsyncSession, variante_id:int):
    result = await db.execute(select(Producto_Variante).where(Producto_Variante.id == variante_id))

    variante = result.scalar_one_or_none()

    if not variante:
        return False
    
    if not variante.disponible:
        return False
    
    variante.disponible = False
    await db.commit()
    return True

