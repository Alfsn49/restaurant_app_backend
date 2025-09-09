from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.sucursal import Sucursal
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from fastapi import HTTPException

class ClienteExistenteError(Exception):
    pass

async def create_Cliente(db: AsyncSession, cliente_data:ClienteCreate):
    
    #Obtener el local_id desde la sucursal enviada
    local_query = await db.execute(select(Sucursal.local_id).where(Sucursal.id == cliente_data.sucursal_id))

    local_id = local_query.scalar_one_or_none()

    if local_id is None:
        raise ValueError("Sucursal no encontrada")
    
    cliente_existente_query = await db.execute(select(Cliente).join(Sucursal, Cliente.sucursal_id == Sucursal.id).where(Cliente.ruc_cedula == cliente_data.ruc_cedula).where(Sucursal.local_id == local_id))
    cliente_existente = cliente_existente_query.scalars().first()

    if cliente_existente:
        raise ClienteExistenteError("El cliente ya está registrado en este local")

    new_cliente = Cliente(**cliente_data)

    db.add(new_cliente)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise

    await db.refresh(new_cliente)
    return new_cliente


async def get_cliente_by_id(db:AsyncSession, cliente_id:str):
    result = await db.execute(select(Cliente).where(Cliente.id == cliente_id))

    return result.scalars().one_or_none()

async def get_cliente_by_DNI(db: AsyncSession, cliente_dni:str):
    result = await db.execute(select(Cliente).where(Cliente.ruc_cedula == cliente_dni))

    return result.scalars().one_or_none()

async def get_clients(db: AsyncSession):
    result = await db.execute(select(Cliente))
    return result.scalars().all()

async def update_cliente(db:AsyncSession, cliente_id:str, cliente_data: ClienteUpdate):
    query =(select(Cliente).where(Cliente.id == cliente_id).where(Cliente.sucursal_id == cliente_data.sucursal_id))
    result = await db.execute(query)
    cliente = result.scalar_one_or_none()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado en esta sucursal")

    # Actualizar solo campos enviados (exclude_unset=True para que no modifique campos no enviados)
    for key, value in cliente_data.model_dump(exclude_unset=True).items():
        setattr(cliente, key, value)

    await db.commit()
    await db.refresh(cliente)

    return cliente

async def soft_delete_cliente(db:AsyncSession, cliente_id:str, sucursal_id: str):
    result = await db.execute(
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
    await db.commit()
    return True
