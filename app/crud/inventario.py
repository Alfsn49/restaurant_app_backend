from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.inventario import Inventario
from app.schemas.inventario import InventarioCreate, InventarioUpdate, InventarioOut

async def create_inventario(db: AsyncSession, inventario_data:InventarioCreate):
    new_inventario = Inventario(**inventario_data)
    db.add(new_inventario)

    await db.commit()
    await db.refresh(new_inventario)
    return new_inventario

async def get_inventario_by_id(db: AsyncSession, inventario_id: str):
    result = await db.execute(select(Inventario).where(Inventario.id == inventario_id))
    return result.scalars().one_or_none()

async def get_inventarios(db: AsyncSession):
    result = await db.execute(select(Inventario))
    return result.scalars().all()

async def update_inventario(db: AsyncSession, inventario_id: str, inventario_data: InventarioUpdate):
    inventario = await get_inventario_by_id(db, inventario_id)

    if not inventario:
        return None
    
    update_inventario = inventario_data.model_dump(exclude_unset=True)

    for key, value in update_inventario.items():
        setattr(inventario, key, value)

    await db.commit()
    await db.refresh(inventario)
    return inventario