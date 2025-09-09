from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils.sdkImage import upload_image_from_bytes, delete_image_by_url  
from app.models.local import Local
from app.schemas.local import LocalCreate, LocalUpdate

async def create_local(db: AsyncSession, name:str, ruc:str, direccion:str, telefono:str, image_file=None):
    image_url = None

    if image_file:
        try:
            image_url = upload_image_from_bytes(
                file_bytes=image_file, 
                public_id=f"local_{name}.jpg"
            )
        except Exception as e:
            # Limpiar cualquier archivo temporal si existe
            raise RuntimeError(f"Error uploading image: {str(e)}")

    new_local = Local(name=name, ruc=ruc, direccion= direccion, telefono= telefono, image=image_url)
    db.add(new_local)
    await db.commit()
    await db.refresh(new_local)
    return new_local

async def get_local_by_id(db: AsyncSession, id:int):
    result = await db.execute(select(Local).where(Local.id == id))
    return result.scalars().one_or_none()

async def get_local_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Local).where(Local.name == name))
    return result.scalars().one_or_none()

async def get_locals(db: AsyncSession):
    result = await db.execute(select(Local))
    return result.scalars().all()

async def update_local(db: AsyncSession, local_id: str, local_data: LocalUpdate):
    local = await get_local_by_id(db, local_id)

    if not local:
        return None

    update_local = local_data.model_dump(exclude_unset=True)

    for key, value in update_local.items():
        setattr(local, key, value)

    await db.commit()
    await db.refresh(local)
    return local

async def soft_delete_local(db: AsyncSession, local_id: str):
    result = await db.execute(select(Local).where(Local.id == local_id, Local.is_active == True))

    local = result.scalars().one_or_none()

    if not local:
        return False
    
    local.is_active = False

    await db.commit()

    return True
    