from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import SessionLocal, get_db
from app.schemas.inventario import InventarioCreate, InventarioOut, InventarioUpdate
from app.crud.inventario import (
    create_inventario,
    get_inventario_by_id,
    get_inventarios,
    update_inventario,
)

router = APIRouter(prefix="/inventarios", tags=["Inventarios"])

@router.post("/", response_model=InventarioOut, status_code=status.HTTP_201_CREATED)
async def create_new_inventario(data: InventarioCreate, db: AsyncSession = Depends(get_db)):
    nuevo_inventario = await create_inventario(db, data)
    return nuevo_inventario

@router.get("/", response_model=List[InventarioOut])
async def read_inventarios(db: AsyncSession = Depends(get_db)):
    inventarios = await get_inventarios(db)
    return inventarios

@router.get("/{inventario_id}", response_model=InventarioOut)
async def read_inventario(inventario_id: str, db: AsyncSession = Depends(get_db)):
    inventario = await get_inventario_by_id(db, inventario_id)
    if not inventario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventario no encontrado")
    return inventario

@router.put("/{inventario_id}", response_model=InventarioOut)
async def update_inventario_data(inventario_id: str, data: InventarioUpdate, db: AsyncSession = Depends(get_db)):
    inventario = await update_inventario(db, inventario_id, data)
    if not inventario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventario no encontrado")
    return inventario
