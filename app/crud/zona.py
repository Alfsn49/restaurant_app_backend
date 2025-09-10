from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.zona import Zona
from app.schemas.zona import ZonaCreate, ZonaUpdate, ZonaOut


def create_zona(db: Session, name: str, sucursal_id: str):
    new_zona = Zona(name=name, sucursal_id=sucursal_id)
    db.add(new_zona)
    db.commit()
    db.refresh(new_zona)
    return new_zona


def get_zona_by_id(db: Session, id: str):
    result = db.execute(select(Zona).where(Zona.id == id))
    return result.scalars().one_or_none()


def get_zona_by_name(db: Session, name: str):
    result = db.execute(select(Zona).where(Zona.name == name))
    return result.scalars().one_or_none()


def get_zona_by_sucursal(db: Session, sucursal_id: str):
    result = db.execute(select(Zona).where(Zona.sucursal_id == sucursal_id))
    return result.scalars().all()


def get_zonas(db: Session):
    result = db.execute(select(Zona))
    return result.scalars().all()


def update_zona(db: Session, zona_id: str, zona_data: ZonaUpdate):
    zona = get_zona_by_id(db, zona_id)

    if not zona:
        return None

    update_fields = zona_data.model_dump(exclude_unset=True)

    for key, value in update_fields.items():
        setattr(zona, key, value)

    db.commit()
    db.refresh(zona)
    return zona
