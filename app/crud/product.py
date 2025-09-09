from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, outerjoin
from app.models.product import Product
from app.models.producto_variante import Producto_Variante
from app.models.sucursal import Sucursal
from app.models.zona import Zona
from app.models.local import Local
from app.schemas.product import ProductoCreate, ProductoOut, ProductoUpdate

from sqlalchemy.orm import selectinload

async def create_product(db: AsyncSession, product_data: ProductoCreate):
    sucursal = await db.get(Sucursal, product_data.sucursal_id)
    if not sucursal:
        raise ValueError("La sucursal no existe")

    stmt = (
        select(Product)
        .join(Sucursal, Product.sucursal_id == Sucursal.id)
        .where(
            Product.nombre == product_data.nombre,
            Sucursal.local_id == sucursal.local_id
        )
    )

    result = await db.execute(stmt)
    existing_product = result.scalars().first()

    if existing_product:
        return None
    
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    # Recargar con relaciones
    stmt = (
        select(Product)
        .options(
            selectinload(Product.categoria),
            selectinload(Product.variantes)
        )
        .where(Product.id == new_product.id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_products_sucursal(db: AsyncSession, sucursal_id: str):
    stmt = (
        select(Product)
        .outerjoin(Product.variantes)  # incluir productos sin variantes
        .outerjoin(Producto_Variante.zona)
        .outerjoin(Zona.sucursal)
        .where((Sucursal.id == sucursal_id) | (Sucursal.id == None))  # incluir productos sin sucursal
        .options(
            selectinload(Product.categoria),
            selectinload(Product.variantes)
                .selectinload(Producto_Variante.inventario),
            selectinload(Product.variantes)
                .selectinload(Producto_Variante.zona)
                .selectinload(Zona.sucursal)
                .selectinload(Sucursal.local)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def list_products_menu(db: AsyncSession, sucursal_id:str):
    print("Sucursal",sucursal_id)
    result = await db.execute(select(Product).options(selectinload(Product.categoria),selectinload(Product.variantes).selectinload(Producto_Variante.inventario),selectinload(Product.variantes).selectinload(Producto_Variante.zona).selectinload(Zona.sucursal).selectinload(Sucursal.local)).where(Product.sucursal_id == sucursal_id))
    return result.scalars().all()

async def get_product_id(db: AsyncSession, product_id: str):
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalars().one_or_none()

async def update_product(db:AsyncSession, product_id: str, product_data: ProductoUpdate):
    product = await get_product_id(db, product_id)

    if not product:
        return None
    
    if product_data.nombre:
        sucursal = await db.get(Sucursal, product.sucursal_id)
        stmt = (
            select(Product)
            .join(Sucursal, Product.sucursal_id == Sucursal.id).where(
                Product.nombre == product_data.nombre,
                Product.sucursal_id == product_data.sucursal_id,
                Sucursal.local_id == sucursal.local_id,
                Product.id != product_id
            )
        )
        result = await db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            return "duplicado"


    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product

async def soft_delete_product(db: AsyncSession, product_id:str):
    result = await db.execute(select(Product).where(Product.id == product_id))

    producto = result.scalars().one_or_none()

    if not producto:
        return False
    
    producto.disponible = False

    await db.commit()

    return True
