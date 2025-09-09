from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.core.database import SessionLocal
from app.crud.categoria import create_categoria, get_categoria_by_name, update_categoria as crud_update_categoria, list_categorias as crud_list_categorias


router = APIRouter(prefix="/categoria", tags=["Categoria"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/create", response_model=CategoriaOut)
async def create_categoria_route(categoria: CategoriaCreate, db: AsyncSession = Depends(get_db)):
    db_categoria = await get_categoria_by_name(db, categoria.name)
    if db_categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta categoria ya existe")
    
    return await create_categoria(db, categoria.name)

@router.get("/list_categoria", response_model=List[CategoriaOut])
async def list_categorias_route(db: AsyncSession = Depends(get_db)):
    categorias = await crud_list_categorias(db)
    if not categorias:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categorias no encontradas")
    
    return categorias

@router.patch("/update_categoria/{categoria_id}", response_model=CategoriaOut)
async def update_categoria_route(categoria_id: str, categoria_data: CategoriaUpdate, db: AsyncSession = Depends(get_db)):
    categoria = await crud_update_categoria(db, categoria_data, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    return categoria