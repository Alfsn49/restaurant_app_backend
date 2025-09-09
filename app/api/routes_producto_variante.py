from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.producto_variante import Producto_Variante_Create, Producto_Variante_Out, Producto_Variante_Update
from app.crud.producto_variante import create_producto_variante, list_productos_variantes, specific_producto_variante, update_variante, delete_soft_producto

router = APIRouter(prefix="/productsVariantes", tags=["Productos_Variantes"])

@router.post("/create", response_model=Producto_Variante_Out, status_code=status.HTTP_201_CREATED)
async def create_variante(
    nombre: str = Form(...),precio: float = Form(...), producto_id: str = Form(...),menu_id: int = Form(...), zona_id:int = Form(...), cantidad:int = Form(...), image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:

        image_bytes= await image.read() if image else None

        producto = await create_producto_variante(db, nombre= nombre, precio= precio, producto_id=producto_id, menu_id=menu_id, zona_id=zona_id, cantidad=cantidad, image_file=image_bytes)
        if producto is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un producto variante con ese nombre en la misma sucursal y local."
            )
        return producto
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el producto variante: {str(e)}"
        )

@router.get("/", response_model=List[Producto_Variante_Out])
async def get_variantes(db: AsyncSession = Depends(get_db)):
    variantes = await list_productos_variantes(db)
    return variantes

@router.get("/{variante_id}", response_model=Producto_Variante_Out)
async def get_variante(variante_id: int, db: AsyncSession = Depends(get_db)):
    variante = await specific_producto_variante(db, variante_id)
    if not variante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto variante no encontrado")
    return variante

@router.patch("/update_producto_variante/{variante_id}")
async def update_variante_endpoint(
    variante_id: int,
    nombre: str = Form(...),precio: float = Form(...), producto_id: str = Form(...),menu_id: int = Form(...), disponible: bool = Form(False), zona_id:int = Form(...), cantidad:int = Form(...), image: UploadFile = File(None), image_url: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        image_bytes = await image.read() if image else None

        updated_variante = await update_variante(db, variante_id, nombre=nombre, precio=precio, producto_id=producto_id, menu_id=menu_id, disponible=disponible ,zona_id=zona_id, cantidad=cantidad, image_file=image_bytes, image_url=image_url)
        if updated_variante is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto variante no encontrado")
        if updated_variante == "duplicado":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nombre duplicado en la misma sucursal y local")
        return{
            "message" : "Usuario actualizado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el producto: {str(e)}"
        )

    
@router.patch("/restaurar_producto_variante/{}")

@router.delete("/delete/{variante_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_variante(variante_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_soft_producto(db, variante_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto variante no encontrado o ya está inactivo")
    return None