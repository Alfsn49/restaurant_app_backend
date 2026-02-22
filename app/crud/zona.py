from sqlalchemy.orm import Session
from sqlalchemy import and_, select, text
from sqlalchemy.exc import IntegrityError
from app.models.zona import Zona
from app.schemas.zona import ZonaCreate, ZonaUpdate, ZonaOut


def create_zona(db: Session, name: str, sucursal_id: str):
    try:
        # Verificar si ya existe una zona con ese nombre en la sucursal
        existing_zona = db.execute(
            select(Zona).where(
                and_(
                    Zona.name == name,
                    Zona.sucursal_id == sucursal_id,
                    Zona.is_active == True
                )
            )
        ).scalar_one_or_none()
        
        if existing_zona:
            print(f"⚠️ La zona '{name}' ya existe en sucursal {sucursal_id} con ID {existing_zona.id}")
            return existing_zona
        
        # Crear nueva zona (deja que la BD asigne el ID)
        new_zona = Zona(
            name=name, 
            sucursal_id=sucursal_id,
            is_active=True
        )
        
        db.add(new_zona)
        db.commit()
        db.refresh(new_zona)
        print(f"✅ Zona creada: ID={new_zona.id}, Nombre={new_zona.name}")
        return new_zona
        
    except IntegrityError as e:
        db.rollback()
        print(f"🔥 IntegrityError: {e.orig}")
        
        # Si es error de clave primaria, intentar una vez más (la secuencia se actualizará sola)
        if "duplicate key" in str(e.orig).lower() and "pkey" in str(e.orig).lower():
            print("⚠️ Problema con secuencia, reintentando...")
            
            # Forzar actualización de secuencia
            db.execute(text("SELECT setval('zonas_id_seq', (SELECT MAX(id) FROM zonas))"))
            db.commit()
            
            # Reintentar la inserción
            new_zona = Zona(name=name, sucursal_id=sucursal_id, is_active=True)
            db.add(new_zona)
            db.commit()
            db.refresh(new_zona)
            return new_zona
            
        return None


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
