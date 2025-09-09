from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.menu import Menu
from app.models.sucursal import Sucursal
from app.schemas.menu import MenuCreate, MenuOut, MenuUpdate


async def create_menu(db: AsyncSession, menu_data: MenuCreate):
    # Verificar duplicado por sucursal + nombre + horario
    result = await db.execute(
        select(Menu).options(selectinload(Menu.sucursal)) .where(
            and_(
                Menu.name == menu_data.name,
                Menu.sucursal_id == menu_data.sucursal_id,
                Menu.horario == menu_data.horario,
                Menu.is_active == True
            )
        )
    )
    existing_menu = result.scalars().first()

    if existing_menu:
        return None  # 🚨 ya existe

    new_menu = Menu(**menu_data.model_dump())
    db.add(new_menu)

    try:
        await db.commit()
        await db.refresh(new_menu)
    except IntegrityError:
        await db.rollback()
        return None

    return new_menu


async def get_menus_by_sucursal(db:AsyncSession, sucursal_id:str):
    result = await db.execute(select(Menu).where(Menu.sucursal_id == sucursal_id))
    return result.scalars().all()

async def get_menu_by_id(db: AsyncSession, menu_id: str):
    result = await db.execute(
        select(Menu).options(selectinload(Menu.sucursal)).where(Menu.id == menu_id, Menu.is_active == True)
    )
    return result.scalars().one_or_none()


async def get_menus(db: AsyncSession):
    result = await db.execute(select(Menu).options(selectinload(Menu.sucursal).selectinload(Sucursal.local) ).where(Menu.is_active == True))
    return result.scalars().all()


async def update_menu(db: AsyncSession, menu_data: MenuUpdate, menu_id: str):
    menu = await get_menu_by_id(db, menu_id)

    if not menu:
        return None
    
    for key, value in menu_data.model_dump(exclude_unset=True).items():
        setattr(menu, key, value)
    
    await db.commit()
    await db.refresh(menu)
    return menu


async def soft_delete_menu(db: AsyncSession, menu_id: str):
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalars().one_or_none()

    if not menu:
        return None
    
    menu.is_active = False
    await db.commit()
    return True
