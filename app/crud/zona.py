from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.zona import Zona
from app.schemas.zona import ZonaCreate, ZonaUpdate, ZonaOut

async def create_zona(db: AsyncSession, name: str, sucursal_id: str):
    new_zona = Zona(name=name, sucursal_id=sucursal_id)
    db.add(new_zona)
    await db.commit()
    await db.refresh(new_zona)
    return new_zona

async def get_zona_by_id(db: AsyncSession, id: str):
    result = await db.execute(select(Zona).where(Zona.id == id))
    return result.scalars().one_or_none()

async def get_zona_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Zona).where(Zona.name == name))
    return result.scalars().one_or_none()

async def get_zona_by_sucursal(db: AsyncSession, sucursal_id: str):
    result = await db.execute(select(Zona).where(Zona.sucursal_id == sucursal_id))
    return result.scalars().all()

async def get_zonas(db: AsyncSession):
    result = await db.execute(select(Zona))
    return result.scalars().all()

async def update_zona(db: AsyncSession, zona_id: str, zona_data: ZonaUpdate):
    zona = await get_zona_by_id(db, zona_id)

    if not zona:
        return None
    
    update_zona = zona_data.model_dump(exclude_unset=True)

    for key, value in update_zona.items():
        setattr(zona, key, value)
    
    await db.commit()
    await db.refresh(zona)
    return zona

