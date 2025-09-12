from sqlalchemy.orm import Session, selectinload  # Cambiado de AsyncSession a Session
from sqlalchemy import select
from app.utils.sdkImage import upload_image_from_bytes, delete_image_by_url  
from app.models.user import User
from app.models.sucursal import Sucursal
from app.models.rol import Rol
from app.schemas.user import UserUpdate
from app.utils.auth import hash_password

def get_user_by_username(db: Session, username: str):  # Quitado async, cambiado a Session
    result = db.execute(  # Quitado await
        select(User)
        .options(
            selectinload(User.sucursal).selectinload(Sucursal.local),
            selectinload(User.rol)
        )
        .where(User.username == username)
    )
    return result.scalars().first()

def get_user_by_id(db: Session, id_user: str):  # Quitado async, cambiado a Session
    result = db.execute(  # Quitado await
        select(User)
        .options(
            selectinload(User.sucursal).selectinload(Sucursal.local),
            selectinload(User.rol)
        )
        .where(User.id == id_user)
    )
    return result.scalars().first()

def create_user(db: Session, username: str, password: str, email: str, name: str, last_name: str, rol_id: int, sucursal_id: int, image_file=None):  # Quitado async, cambiado a Session
    image_url = None

    if image_file:
        try:
            image_url = upload_image_from_bytes(
                file_bytes=image_file,
                public_id=f"users_{name}",
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
        image=image_url,
        sucursal_id=sucursal_id
    )
    db.add(new_user)
    db.commit()  # Quitado await
    db.refresh(new_user)  # Quitado await

    # 🔑 Vuelvo a consultar para traer las relaciones
    result = db.execute(  # Quitado await
        select(User)
        .options(
            selectinload(User.rol),
            selectinload(User.sucursal).selectinload(Sucursal.local)
        )
        .where(User.id == new_user.id)
    )
    return result.scalars().first()

def list_users(sucursal_id: str, db: Session):  # Quitado async, cambiado a Session
    result = db.execute(  # Quitado await
        select(User)
        .options(
            selectinload(User.rol),
            selectinload(User.sucursal).selectinload(Sucursal.local)
        )
        .where(User.sucursal_id == sucursal_id)
        .where(User.rol.has(Rol.name.notin_(["Administrador", "Dueño"])))
    )
    return result.scalars().all()

def update_user(
    db: Session,
    user_id: str,
    username: str = None,
    email: str = None,
    name: str = None,
    last_name: str = None,
    sucursal_id: int = None,
    rol_id: int = None,
    image_file=None,
    image_url=None
):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    new_image_url = None

    # Manejo de imagen
    if image_file:
        try:
            if user.image:
                try:
                    delete_image_by_url(user.image)
                except Exception as e:
                    print(f"⚠️ No se pudo borrar la imagen anterior: {str(e)}")
            new_image_url = upload_image_from_bytes(
                file_bytes=image_file,
                public_id=f"users_{username or user.username}_{name or user.name}",
                folder="users"
            )
        except Exception as e:
            raise RuntimeError(f"Error uploading image: {str(e)}")
    elif image_url:
        new_image_url = image_url

    # Solo actualizar campos que no sean None
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if name is not None:
        user.name = name
    if last_name is not None:
        user.last_name = last_name
    if sucursal_id is not None:
        user.sucursal_id = sucursal_id
    if rol_id is not None:
        user.rol_id = rol_id
    if new_image_url is not None:
        user.image = new_image_url

    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user_id: str):  # Quitado async, cambiado a Session
    result = db.execute(select(User).where(User.id == user_id))  # Quitado await
    user = result.scalars().one_or_none()

    if not user:
        return None
    
    user.is_active = False
    db.commit()  # Quitado await
    return True

def get_profile(db: Session, user_id: str):  # Quitado async, cambiado a Session
    result = db.execute(  # Quitado await
        select(User)
        .options(selectinload(User.sucursal).selectinload(Sucursal.local))
        .where(User.id == user_id)
    )
    return result.scalars().one_or_none()