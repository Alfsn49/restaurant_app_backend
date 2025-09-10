from sqlalchemy.orm import Session  # Cambiado de AsyncSession a Session
from sqlalchemy import select
from app.models.inventario import Inventario
from app.schemas.inventario import InventarioCreate, InventarioUpdate, InventarioOut

def create_inventario(db: Session, inventario_data: InventarioCreate):  # Quitado async, cambiado a Session
    new_inventario = Inventario(**inventario_data.model_dump())  # Añadido .model_dump()
    db.add(new_inventario)
    db.commit()  # Quitado await
    db.refresh(new_inventario)  # Quitado await
    return new_inventario

def get_inventario_by_id(db: Session, inventario_id: str):  # Quitado async, cambiado a Session
    result = db.execute(select(Inventario).where(Inventario.id == inventario_id))  # Quitado await
    return result.scalars().one_or_none()

def get_inventarios(db: Session):  # Quitado async, cambiado a Session
    result = db.execute(select(Inventario))  # Quitado await
    return result.scalars().all()

def update_inventario(db: Session, inventario_id: str, inventario_data: InventarioUpdate):  # Quitado async, cambiado a Session
    inventario = get_inventario_by_id(db, inventario_id)  # Quitado await

    if not inventario:
        return None
    
    update_inventario = inventario_data.model_dump(exclude_unset=True)

    for key, value in update_inventario.items():
        setattr(inventario, key, value)

    db.commit()  # Quitado await
    db.refresh(inventario)  # Quitado await
    return inventario