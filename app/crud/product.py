from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, and_
from app.models.product import Product
from app.models.producto_variante import Producto_Variante
from app.models.categoria import Categoria
from app.models.sucursal import Sucursal
from app.models.zona import Zona
from app.schemas.product import ProductoCreate, ProductoUpdate
from app.models.inventario import Inventario

def create_product(db: Session, product_data: ProductoCreate):
    sucursal = db.get(Sucursal, product_data.sucursal_id)
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

    result = db.execute(stmt)
    existing_product = result.scalars().first()

    if existing_product:
        return None  # 🚨 producto duplicado en el mismo local
    
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Recargar con relaciones
    stmt = (
        select(Product)
        .options(
            selectinload(Product.categoria),
            selectinload(Product.variantes)
        )
        .where(Product.id == new_product.id)
    )
    result = db.execute(stmt)
    return result.scalars().first()


def list_products_sucursal(db: Session, sucursal_id: str):
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
    result = db.execute(stmt)
    return result.scalars().unique().all()


def list_products_menu(db: Session, sucursal_id: str):
    stmt = (
        select(
            Product.id.label("producto_id"),
            Product.nombre.label("producto_nombre"),
            Product.disponible.label("producto_disponible"),
            Product.categoria_id,
            
            # Datos de categoría
            Categoria.name.label("categoria_nombre"),
            
            # Datos de variante
            Producto_Variante.id.label("variante_id"),
            Producto_Variante.nombre.label("variante_nombre"),
            Producto_Variante.precio,
            Producto_Variante.disponible.label("variante_disponible"),
            Producto_Variante.image,
            Producto_Variante.zona_id,
            
            # Datos de zona
            Zona.name.label("zona_nombre"),
            Zona.id.label("zona_id"),
            
            # Precio mínimo para ordenamiento
            func.min(Producto_Variante.precio).over(
                partition_by=Product.id
            ).label("precio_minimo_producto"),
            
            # Inventario (si lo necesitas)
            func.coalesce(Inventario.cantidad, 0).label("cantidad_inventario")
        )
        .select_from(Product)
        .join(Producto_Variante, Producto_Variante.producto_id == Product.id)
        .join(Categoria, Categoria.id == Product.categoria_id)  # ✅ Join categoría
        .outerjoin(Zona, Zona.id == Producto_Variante.zona_id)  # ✅ Outer join zona
        .outerjoin(
            Inventario, 
            and_(
                Inventario.producto_variante_id == Producto_Variante.id,
                Inventario.sucursal_id == sucursal_id  # ✅ Inventario de esta sucursal
            )
        )
        .where(
            and_(
                Product.sucursal_id == sucursal_id,
                Product.disponible == True,
                Producto_Variante.disponible == True
            )
        )
        .order_by("precio_minimo_producto", Producto_Variante.precio.asc())
    )
    
    result = db.execute(stmt)
    return result.all()


def get_product_id(db: Session, product_id: str):
    result = db.execute(select(Product).where(Product.id == product_id))
    return result.scalars().one_or_none()


def update_product(db: Session, product_id: str, product_data: ProductoUpdate):
    product = get_product_id(db, product_id)

    if not product:
        return None
    
    if product_data.nombre:
        sucursal = db.get(Sucursal, product.sucursal_id)
        stmt = (
            select(Product)
            .join(Sucursal, Product.sucursal_id == Sucursal.id)
            .where(
                Product.nombre == product_data.nombre,
                Product.sucursal_id == product_data.sucursal_id,
                Sucursal.local_id == sucursal.local_id,
                Product.id != product_id
            )
        )
        result = db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            return "duplicado"

    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


def soft_delete_product(db: Session, product_id: str):
    result = db.execute(select(Product).where(Product.id == product_id))
    producto = result.scalars().one_or_none()

    if not producto:
        return False
    
    producto.disponible = False
    db.commit()

    return True
