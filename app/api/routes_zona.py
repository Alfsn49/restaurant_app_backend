from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal, get_db
from app.schemas.zona import ZonaCreate, ZonaUpdate, ZonaOut
from app.crud.zona import create_zona, get_zonas, get_zona_by_id, get_zona_by_name, update_zona, get_zona_by_sucursal

router = APIRouter(prefix="/zonas", tags=["Zonas"])

@router.get("/get-zonas", response_model=list[ZonaOut])
async def list_zonas(db: AsyncSession = Depends(get_db)):
    zonas = await get_zonas(db)
    return zonas

@router.post("/create-zona", response_model=ZonaOut, status_code=status.HTTP_201_CREATED)
async def create_new_zona(zona: ZonaCreate, db: AsyncSession = Depends(get_db)):
    print("Datos recibidos", zona)
    existing_zona = await get_zona_by_name(db, zona.name)

    if existing_zona:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="La zona ya existe")
    
    return await create_zona(db, zona.name, zona.sucursal_id)

@router.get("/get-zona/{zona_id}", response_model=ZonaOut)
async def get_zona(zona_id: str, db: AsyncSession = Depends(get_db)):
    zona = await get_zona_by_id(db, zona_id)

    if not zona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona no encontrada")
    
    return zona

@router.get("/get-zona-by-sucursal/{sucursal_id}", response_model=list[ZonaOut])
async def list_zonas_by_sucursal(sucursal_id: str, db:AsyncSession = Depends(get_db)):
    return await get_zona_by_sucursal(db, sucursal_id)

@router.put("/update-zona/{zona_id}", response_model=ZonaOut)
async def update_existing_zona(zona_id: str, zona_data: ZonaUpdate, db: AsyncSession = Depends(get_db)):
    zona = await get_zona_by_id(db, zona_id)

    if not zona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona no encontrada")
    
    updated_zona = await update_zona(db, zona_id, zona_data)
    return updated_zona