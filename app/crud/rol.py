from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.rol import Rol
from app.schemas.rol import RolUpdate

async def create_rol(db: AsyncSession, name: str, description: str = None):

    new_rol = Rol(name=name, description=description)
    db.add(new_rol)
    await db.commit()
    await db.refresh(new_rol)
    return new_rol

async def get_rol_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Rol).where(Rol.name == name))
    print("Ver rol", result)
    return result.scalars().one_or_none()

async def get_rols(db: AsyncSession):
    result = await db.execute(select(Rol).where(Rol.name.notin_(["Administrador", "Dueño"])))
    return result.scalars().all()


async def get_rol_by_id(db: AsyncSession, id:int):
    result = await db.execute(select(Rol).where(Rol.id == id))
    return result.scalars().one_or_none()

async def update_rol(db: AsyncSession, rol_id: int, rol_data: RolUpdate):
    rol = await get_rol_by_id(db, rol_id)

    if not rol:
        return None
    
    update_data = rol_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(rol, key, value)

    await db.commit()
    await db.refresh(rol)
    return rol
