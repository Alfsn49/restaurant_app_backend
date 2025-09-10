from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session  # Cambiado de AsyncSession a Session
from typing import List
from app.core.database import get_db  # Importamos get_db sincrónico
from app.schemas.inventario import InventarioCreate, InventarioOut, InventarioUpdate
from app.crud.inventario import (
    create_inventario,
    get_inventario_by_id,
    get_inventarios,
    update_inventario,
)

router = APIRouter(prefix="/inventarios", tags=["Inventarios"])

@router.post("/", response_model=InventarioOut, status_code=status.HTTP_201_CREATED)
def create_new_inventario(data: InventarioCreate, db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    nuevo_inventario = create_inventario(db, data)  # Quitado await
    return nuevo_inventario

@router.get("/", response_model=List[InventarioOut])
def read_inventarios(db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    inventarios = get_inventarios(db)  # Quitado await
    return inventarios

@router.get("/{inventario_id}", response_model=InventarioOut)
def read_inventario(inventario_id: str, db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    inventario = get_inventario_by_id(db, inventario_id)  # Quitado await
    if not inventario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventario no encontrado")
    return inventario

@router.put("/{inventario_id}", response_model=InventarioOut)
def update_inventario_data(inventario_id: str, data: InventarioUpdate, db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    inventario = update_inventario(db, inventario_id, data)  # Quitado await
    if not inventario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventario no encontrado")
    return inventario