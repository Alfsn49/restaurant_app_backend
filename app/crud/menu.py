from sqlalchemy import and_
from sqlalchemy.orm import selectinload, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from app.models.menu import Menu
from app.models.sucursal import Sucursal
from app.schemas.menu import MenuCreate, MenuOut, MenuUpdate


def create_menu(db: Session, menu_data: MenuCreate):
    # Verificar duplicado por sucursal + nombre + horario
    result = db.execute(
        select(Menu).options(selectinload(Menu.sucursal)).where(
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
        db.commit()
        db.refresh(new_menu)
    except IntegrityError:
        db.rollback()
        return None

    return new_menu


def get_menus_by_sucursal(db: Session, sucursal_id: str):
    result = db.execute(select(Menu).where(Menu.sucursal_id == sucursal_id))
    return result.scalars().all()


def get_menu_by_id(db: Session, menu_id: str):
    result = db.execute(
        select(Menu).options(selectinload(Menu.sucursal)).where(Menu.id == menu_id, Menu.is_active == True)
    )
    return result.scalars().one_or_none()


def get_menus(db: Session):
    result = db.execute(
        select(Menu).options(selectinload(Menu.sucursal).selectinload(Sucursal.local)).where(Menu.is_active == True)
    )
    return result.scalars().all()


def update_menu(db: Session, menu_data: MenuUpdate, menu_id: str):
    menu = get_menu_by_id(db, menu_id)

    if not menu:
        return None

    for key, value in menu_data.model_dump(exclude_unset=True).items():
        setattr(menu, key, value)

    db.commit()
    db.refresh(menu)
    return menu


def soft_delete_menu(db: Session, menu_id: str):
    result = db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalars().one_or_none()

    if not menu:
        return None

    menu.is_active = False
    db.commit()
    return True
