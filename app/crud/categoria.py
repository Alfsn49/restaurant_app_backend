from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaUpdate

async def create_categoria(db: AsyncSession, name: str):
    existing = await get_categoria_by_name(db, name)
    if existing:
        return existing  # o lanzar una excepción si no quieres duplicados

    new_categoria = Categoria(name=name)
    db.add(new_categoria)
    await db.commit()
    await db.refresh(new_categoria)
    return new_categoria

async def get_categoria_by_id(db: AsyncSession, categoria_id:str):
    result = await db.execute(select(Categoria).where(Categoria.id == categoria_id))

async def get_categoria_by_name(db: AsyncSession, name: str):
    query = select(Categoria).where(Categoria.name == name)
    result = await db.execute(query)
    categoria = result.scalars().first()
    return categoria

async def list_categorias(db:AsyncSession):
    result = await db.execute(select(Categoria))
    return result.scalars().all()

async def update_categoria(db:AsyncSession, categoria_data: CategoriaUpdate, categoria_id:str):
    categoria = await get_categoria_by_id(db, categoria_id)

    if not categoria:
        return None
    
    update_categoria = categoria_data.model_dump(exclude_unset=True)

    for key, value in update_categoria.items():
        setattr(categoria, key, value)

    await db.commit()
    await db.refresh(categoria)
    return categoria