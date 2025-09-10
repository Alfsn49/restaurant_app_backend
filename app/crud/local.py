from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.utils.sdkImage import upload_image_from_bytes, delete_image_by_url  
from app.models.local import Local
from app.schemas.local import LocalCreate, LocalUpdate

# ✅ Crear local
def create_local(db: Session, name: str, ruc: str, direccion: str, telefono: str, image_file=None):
    image_url = None

    if image_file:
        try:
            image_url = upload_image_from_bytes(
                file_bytes=image_file, 
                public_id=f"local_{name}.jpg"
            )
        except Exception as e:
            raise RuntimeError(f"Error uploading image: {str(e)}")

    new_local = Local(
        name=name, 
        ruc=ruc, 
        direccion=direccion, 
        telefono=telefono, 
        image=image_url
    )
    db.add(new_local)
    db.commit()
    db.refresh(new_local)
    return new_local

# ✅ Obtener local por ID
def get_local_by_id(db: Session, id: int):
    result = db.execute(select(Local).where(Local.id == id))
    return result.scalars().one_or_none()

# ✅ Obtener local por nombre
def get_local_by_name(db: Session, name: str):
    result = db.execute(select(Local).where(Local.name == name))
    return result.scalars().one_or_none()

# ✅ Obtener todos los locales
def get_locals(db: Session):
    result = db.execute(select(Local))
    return result.scalars().all()

# ✅ Actualizar local
def update_local(db: Session, local_id: int, local_data: LocalUpdate):
    local = get_local_by_id(db, local_id)

    if not local:
        return None

    update_data = local_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(local, key, value)

    db.commit()
    db.refresh(local)
    return local

# ✅ Borrado lógico (soft delete)
def soft_delete_local(db: Session, local_id: int):
    result = db.execute(select(Local).where(Local.id == local_id, Local.is_active == True))
    local = result.scalars().one_or_none()

    if not local:
        return False
    
    local.is_active = False
    db.commit()

    return True
