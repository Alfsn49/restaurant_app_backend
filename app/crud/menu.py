from sqlalchemy import and_
from sqlalchemy.orm import selectinload, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from app.models.menu import Menu
from app.models.sucursal import Sucursal
from app.schemas.menu import MenuCreate, MenuOut, MenuUpdate


def create_menu(db: Session, menu_data: MenuCreate):
    try:
        # Log para ver qué estás intentando crear
        print(f"Intentando crear menú: {menu_data.name} para sucursal: {menu_data.sucursal_id}")
        
        # Verificar duplicado
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
            print(f"❌ Menú duplicado encontrado: ID {existing_menu.id}")
            return None

        new_menu = Menu(**menu_data.model_dump())
        db.add(new_menu)
        db.commit()
        db.refresh(new_menu)
        print(f"✅ Menú creado exitosamente: ID {new_menu.id}")
        return new_menu

    except IntegrityError as e:
        db.rollback()
        print(f"🔥 IntegrityError: {str(e)}")  # Esto te dirá exactamente qué constraint se violó
        return None
    except Exception as e:
        db.rollback()
        print(f"🔥 Error inesperado: {str(e)}")
        return None

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
