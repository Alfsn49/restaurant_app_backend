from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import tempfile
import os
from app.models.sucursal import Sucursal
from app.schemas.sucursal import SucursalCreate, SucursalUpdate, SucursalOut


async def create_sucursal(db: AsyncSession, nombre, direccion, ruc, telefono, local_id):
    
    new_sucursal = Sucursal(
        nombre=nombre,
        direccion=direccion,
        ruc=ruc,
        telefono=telefono,
        local_id=local_id,
    )
    db.add(new_sucursal)
    await db.commit()
    await db.refresh(new_sucursal)
    return new_sucursal

async def get_sucursal_by_id_local(id_local:str, db: AsyncSession):
    result = await db.execute(select(Sucursal).where(Sucursal.local_id == id_local))
    return result.scalars().all()

async def get_sucursal_by_id(db: AsyncSession, id:str):
    result = await db.execute(select(Sucursal).where(Sucursal.id == id))
    return result.scalars().one_or_none()

async def get_sucursal_by_name(db: AsyncSession, nombre: str):
    result = await db.execute(select(Sucursal).where(Sucursal.nombre == nombre))

    return result.scalars().one_or_none()

async def get_sucursales(db: AsyncSession):
    result = await db.execute(select(Sucursal).options(selectinload(Sucursal.local)))
    return result.scalars().all()

async def update_sucursal(db: AsyncSession, sucursal_id: str, sucursal_data: SucursalUpdate):
    sucursal = await get_sucursal_by_id(db, sucursal_id)

    if not sucursal:
        return None
    
    update_sucursal = sucursal_data.model_dump(exclude_unset=True)

    for key, value in update_sucursal.items():
        setattr(sucursal, key, value)

    await db.commit()
    await db.refresh(sucursal)
    return sucursal

async def soft_delete_sucursal(db: AsyncSession, sucursal_id: str):
    result = await db.execute(select(Sucursal).where(Sucursal.id == sucursal_id, Sucursal.is_active == True))

    sucursal = result.scalars().one_or_none()

    if not sucursal:
        return None
    
    sucursal.is_active = False

    await db.commit()

    return True