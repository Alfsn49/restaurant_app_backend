from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
import tempfile
import os
from app.models.sucursal import Sucursal
from app.schemas.sucursal import SucursalCreate, SucursalUpdate, SucursalOut


def create_sucursal(db: Session, nombre, direccion, ruc, telefono, local_id):
    new_sucursal = Sucursal(
        nombre=nombre,
        direccion=direccion,
        ruc=ruc,
        telefono=telefono,
        local_id=local_id,
    )
    db.add(new_sucursal)
    db.commit()
    db.refresh(new_sucursal)
    return new_sucursal


def get_sucursal_by_id_local(id_local: str, db: Session):
    result = db.execute(select(Sucursal).where(Sucursal.local_id == id_local))
    return result.scalars().all()


def get_sucursal_by_id(db: Session, id: str):
    result = db.execute(select(Sucursal).where(Sucursal.id == id))
    return result.scalars().one_or_none()


def get_sucursal_by_name(db: Session, nombre: str):
    result = db.execute(select(Sucursal).where(Sucursal.nombre == nombre))
    return result.scalars().one_or_none()


def get_sucursales(db: Session):
    result = db.execute(select(Sucursal).options(selectinload(Sucursal.local)))
    return result.scalars().all()


def update_sucursal(db: Session, sucursal_id: str, sucursal_data: SucursalUpdate):
    sucursal = get_sucursal_by_id(db, sucursal_id)

    if not sucursal:
        return None

    update_data = sucursal_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(sucursal, key, value)

    db.commit()
    db.refresh(sucursal)
    return sucursal


def soft_delete_sucursal(db: Session, sucursal_id: str):
    result = db.execute(select(Sucursal).where(Sucursal.id == sucursal_id, Sucursal.is_active == True))
    sucursal = result.scalars().one_or_none()

    if not sucursal:
        return None

    sucursal.is_active = False
    db.commit()
    return True
