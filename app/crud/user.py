from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.utils.sdkImage import upload_image_from_bytes, delete_image_by_url  
from app.models.user import User
from app.models.sucursal import Sucursal
from app.models.rol import Rol
from app.schemas.user import UserUpdate
from app.utils.auth import hash_password

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).options(selectinload(User.sucursal).selectinload(Sucursal.local),selectinload(User.rol)).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(db:AsyncSession, id_user:str):
    result = await db.execute(select(User).options(selectinload(User.sucursal).selectinload(Sucursal.local),selectinload(User.rol)).where(User.id == id_user))
    return result.scalars().first()



async def create_user(db: AsyncSession,  username: str, password: str, email: str, name: str, last_name:str ,rol_id:int, sucursal_id:int, image_file = None):

    image_url = None

    if image_file:
        try:
            image_url = upload_image_from_bytes(
                file_bytes=image_file,
                public_id=f"users_{name}",  # ✅ Cambiado a public_id
                folder="users"
            )
        except Exception as e:
            raise RuntimeError(f"Error uploading image: {str(e)}")

    new_user = User(
        username=username,
        password=hash_password(password),
        email=email,
        name=name,
        last_name=last_name,
        rol_id=rol_id,
        image = image_url,
        sucursal_id=sucursal_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 🔑 Vuelvo a consultar para traer las relaciones
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.rol),
            selectinload(User.sucursal).selectinload(Sucursal.local)
        )
        .where(User.id == new_user.id)
    )
    return result.scalars().first()

async def list_users(sucursal_id: str, db: AsyncSession):
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.rol),
            selectinload(User.sucursal).selectinload(Sucursal.local)
        )
        .where(User.sucursal_id == sucursal_id)
        .where(User.rol.has(Rol.name.notin_(["Administrador", "Dueño"])))
    )
    return result.scalars().all()

async def update_user(
    db: AsyncSession,
    user_id: str,
    username: str,
    email: str,
    name: str,
    last_name: str,
    sucursal_id: int,
    rol_id: int,
    image_file=None,
    image_url=None
):
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    new_image_url = None

    # Si viene un archivo nuevo → subir y borrar el anterior
    if image_file:
        try:
            # 🔥 Eliminar la imagen anterior si existe
            if user.image:
                try:
                    delete_image_by_url(user.image)
                except Exception as e:
                    print(f"⚠️ No se pudo borrar la imagen anterior: {str(e)}")

            # ✅ CORRECCIÓN: Usar public_id en lugar de file_name
            new_image_url = upload_image_from_bytes(
                file_bytes=image_file,
                public_id=f"users_{username}_{name}",  # ✅ Cambiado a public_id
                folder="users"
            )
        except Exception as e:
            raise RuntimeError(f"Error uploading image: {str(e)}")

    # Si no vino archivo, pero sí pasó URL explícita → se conserva
    elif image_url:
        new_image_url = image_url  

    # Actualizar campos
    user.username = username
    user.email = email
    user.name = name
    user.last_name = last_name
    user.sucursal_id = sucursal_id
    user.rol_id = rol_id

    if new_image_url:
        user.image = new_image_url

    await db.commit()
    await db.refresh(user)
    return user

async def soft_delete_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()


    if not user:
        return None
    
    user.is_active = False
    await db.commit()
    return True


async def get_profile(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(User)
        .options(selectinload(User.sucursal).selectinload(Sucursal.local))
        .where(User.id == user_id)
    )
    return result.scalars().one_or_none()