from sqlalchemy.orm import Session  # Cambiado de AsyncSession a Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.sucursal import Sucursal
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from fastapi import HTTPException

class ClienteExistenteError(Exception):
    pass

def create_Cliente(db: Session, cliente_data: ClienteCreate):  # Quitado async, cambiado a Session
    
    # Obtener el local_id desde la sucursal enviada
    local_query = db.execute(select(Sucursal.local_id).where(Sucursal.id == cliente_data.sucursal_id))  # Quitado await
    local_id = local_query.scalar_one_or_none()

    if local_id is None:
        raise ValueError("Sucursal no encontrada")
    
    cliente_existente_query = db.execute(  # Quitado await
        select(Cliente)
        .join(Sucursal, Cliente.sucursal_id == Sucursal.id)
        .where(Cliente.ruc_cedula == cliente_data.ruc_cedula)
        .where(Sucursal.local_id == local_id)
    )
    cliente_existente = cliente_existente_query.scalars().first()

    if cliente_existente:
        raise ClienteExistenteError("El cliente ya está registrado en este local")

    new_cliente = Cliente(**cliente_data.model_dump())

    db.add(new_cliente)
    try:
        db.commit()  # Quitado await
    except IntegrityError:
        db.rollback()  # Quitado await
        raise

    db.refresh(new_cliente)  # Quitado await
    return new_cliente

def get_cliente_by_id(db: Session, cliente_id: str):  # Quitado async, cambiado a Session
    result = db.execute(select(Cliente).where(Cliente.id == cliente_id))  # Quitado await
    return result.scalars().one_or_none()

def get_cliente_by_DNI(db: Session, cliente_dni: str):  # Quitado async, cambiado a Session
    result = db.execute(select(Cliente).where(Cliente.ruc_cedula == cliente_dni))  # Quitado await
    return result.scalars().one_or_none()

def get_clients(db: Session):  # Quitado async, cambiado a Session
    result = db.execute(select(Cliente))  # Quitado await
    return result.scalars().all()

def update_cliente(db: Session, cliente_id: str, cliente_data: ClienteUpdate):  # Quitado async, cambiado a Session
    query = select(Cliente).where(Cliente.id == cliente_id).where(Cliente.sucursal_id == cliente_data.sucursal_id)
    result = db.execute(query)  # Quitado await
    cliente = result.scalar_one_or_none()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado en esta sucursal")

    # Actualizar solo campos enviados (exclude_unset=True para que no modifique campos no enviados)
    for key, value in cliente_data.model_dump(exclude_unset=True).items():
        setattr(cliente, key, value)

    db.commit()  # Quitado await
    db.refresh(cliente)  # Quitado await

    return cliente

def soft_delete_cliente(db: Session, cliente_id: str, sucursal_id: str):  # Quitado async, cambiado a Session
    result = db.execute(  # Quitado await
        select(Cliente)
        .where(Cliente.id == cliente_id)
        .where(Cliente.sucursal_id == sucursal_id)
    )
    cliente = result.scalar_one_or_none()

    if not cliente:
        return False
    
    if not cliente.is_active:
        return False

    cliente.is_active = False
    db.commit()  # Quitado await
    return True