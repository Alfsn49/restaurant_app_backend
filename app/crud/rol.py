from sqlalchemy.orm import Session, selectinload  # Cambiado de 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.rol import Rol
from app.schemas.rol import RolUpdate

def create_rol(db: Session, name: str, description: str = None):

    new_rol = Rol(name=name, description=description)
    db.add(new_rol)
    db.commit()
    db.refresh(new_rol)
    return new_rol

def get_rol_by_name(db: Session, name: str):
    result = db.execute(select(Rol).where(Rol.name == name))
    print("Ver rol", result)
    return result.scalars().one_or_none()

def get_rols(db: Session):
    result =  db.execute(select(Rol).where(Rol.name.notin_(["Administrador", "Dueño"])))
    return result.scalars().all()


def get_rol_by_id(db: Session, id:int):
    result =  db.execute(select(Rol).where(Rol.id == id))
    return result.scalars().one_or_none()

def update_rol(db: Session, rol_id: int, rol_data: RolUpdate):
    rol = get_rol_by_id(db, rol_id)

    if not rol:
        return None
    
    update_data = rol_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(rol, key, value)

    db.commit()
    db.refresh(rol)
    return rol
