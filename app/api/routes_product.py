from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.product import ProductoCreate, ProductoOut, ProductoUpdate
from app.crud.product import (
    create_product,
    get_product_id,
    list_products_menu,
    update_product,
    soft_delete_product,
    list_products_sucursal,
)
from app.utils.auth import role_required

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/list-menu/{sucursal_id}", response_model=list[dict])
def list_products_endpoint(
    db: Session = Depends(get_db),
    sucursal_id: str | None = None
):
    productos_data = list_products_menu(db, sucursal_id)
    
    if not productos_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen productos para esta sucursal"
        )
    
    # Transformación directa sin lógica compleja
    return [
        {
            "producto_id": row.producto_id,
            "product_variante_id": row.variante_id,
            "nombre": row.variante_nombre or row.producto_nombre,
            "precio": float(row.precio),
            "disponible": row.variante_disponible,
            "cantidad": row.cantidad_inventario,
            "categoria_id": row.categoria_id,
            "categoria": row.categoria_nombre,
            "image": row.image,
            "zona_id": row.zona_id,
            "zona_nombre": row.zona_nombre
        }
        for row in productos_data
    ]


@router.get("/list/{sucursal_id}", response_model=list[dict])
def list_products_by_sucursal(
    sucursal_id: str,
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)
):
    productos = list_products_sucursal(db, sucursal_id)

    if not productos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen productos en esta sucursal"
        )

    resultado = {}

    for producto in productos:
        categoria_id = producto.categoria.id if producto.categoria else None
        categoria_nombre = producto.categoria.name if producto.categoria else "Sin categoría"

        if categoria_id not in resultado:
            resultado[categoria_id] = {
                "categoria_id": categoria_id,
                "categoria": categoria_nombre,
                "productos": []
            }

        prod_dict = {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "disponible": producto.disponible,
            "variantes": []
        }

        if producto.variantes and len(producto.variantes) > 0:
            for variante in producto.variantes:
                cantidad_actual = 0
                if variante.inventario:
                    for inv in variante.inventario:
                        if inv.sucursal_id == sucursal_id:
                            cantidad_actual = inv.cantidad
                            break

                prod_dict["variantes"].append({
                    "producto_variante_id": variante.id,
                    "nombre": variante.nombre,
                    "precio": variante.precio,
                    "disponible": variante.disponible,
                    "cantidad": cantidad_actual,
                    "zona_id": variante.zona_id,
                    "menu_id": variante.menu_id,
                    "image": variante.image,
                    "zona_nombre": variante.zona.name if variante.zona else None,
                    "sucursal_id": sucursal_id
                })

        resultado[categoria_id]["productos"].append(prod_dict)

    return list(resultado.values())


@router.get("/{product_id}", response_model=ProductoOut)
def get_producto(product_id: str, db: Session = Depends(get_db)):
    producto = get_product_id(db, product_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el producto")
    return producto


@router.post("/create", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product_data: ProductoCreate, db: Session = Depends(get_db)):
    nuevo_producto = create_product(db, product_data)
    if not nuevo_producto:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Producto ya existe en la sucursal/local")
    return nuevo_producto


@router.patch("/update_product/{producto_id}", response_model=ProductoOut)
def update_product_data(producto_id: str, producto_data: ProductoUpdate, db: Session = Depends(get_db)):
    producto_actualizado = update_product(db, producto_id, producto_data)
    if producto_actualizado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if producto_actualizado == "duplicado":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de producto duplicado en sucursal/local")
    return producto_actualizado


@router.delete("/delete_product/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_product_endpoint(producto_id: str, db: Session = Depends(get_db)):
    eliminado = soft_delete_product(db, producto_id)
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return None
