from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaUpdate

def create_categoria(db: Session, name: str):
    existing = get_categoria_by_name(db, name)
    if existing:
        return existing  # o lanzar una excepción si no quieres duplicados

    new_categoria = Categoria(name=name)
    db.add(new_categoria)
    db.commit()
    db.refresh(new_categoria)
    return new_categoria

def get_categoria_by_id(db: Session, categoria_id:str):
    result = db.execute(select(Categoria).where(Categoria.id == categoria_id))
    categoria = result.scalars().first()
    return categoria

def get_categoria_by_name(db: Session, name: str):
    query = select(Categoria).where(Categoria.name == name)
    result =  db.execute(query)
    categoria = result.scalars().first()
    return categoria

def list_categorias(db:Session):
    result = db.execute(select(Categoria))
    return result.scalars().all()

def update_categoria(db:Session, categoria_data: CategoriaUpdate, categoria_id:str):
    categoria = get_categoria_by_id(db, categoria_id)

    if not categoria:
        return None
    
    update_categoria = categoria_data.model_dump(exclude_unset=True)

    for key, value in update_categoria.items():
        setattr(categoria, key, value)

    db.commit()
    db.refresh(categoria)
    return categoria