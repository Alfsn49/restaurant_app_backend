from fastapi import APIRouter, Depends, HTTPException, Request, status, Form, UploadFile, File
from sqlalchemy.orm import Session  # Cambiado de AsyncSession a Session
from typing import List
from app.schemas.user import UserCreate, UserLogin, UserOut, UserUpdate
from app.core.database import SessionLocal, get_db  # Importamos get_db sincrónico
from app.crud.user import create_user, get_user_by_username, get_profile, get_user_by_id, list_users, update_user, soft_delete_user
from app.utils.auth import verify_password, create_access_token, get_current_user, create_refresh_token, validate_refresh_token, role_required
from jose import jwt, JWTError

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=dict)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    image: UploadFile = File(None),
    name: str = Form(...),
    last_name: str = Form(...),
    sucursal_id: str = Form(...),
    rol_id: int = Form(...),
    db: Session = Depends(get_db)  # Cambiado a Session
):
    try:
        image_bytes = await image.read() if image else None  # Quitado await

        db_user = get_user_by_username(db, username)  # Quitado await
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        new_user = create_user(  # Quitado await
            db, username=username, password=password, email=email,
            name=name, last_name=last_name, rol_id=rol_id,
            sucursal_id=sucursal_id, image_file=image_bytes
        )
        
        return {"message": "Usuario registrado exitosamente", "id": new_user.id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario: {str(e)}"
        )

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):  # Cambiado a Session
    db_user = get_user_by_username(db, user.username)  # Quitado await
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    access_token = create_access_token({
        "sub": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "name": db_user.name,
        "last_name": db_user.last_name,
        "image": db_user.image,
        "is_active": db_user.is_active,
        "sucursal": {
            "id": db_user.sucursal_id,
            "nombre": db_user.sucursal.nombre
        },
        "local": {
            "id": db_user.sucursal.local.id,
            "nombre": db_user.sucursal.local.name
        },
        "rol": {
            "id": db_user.rol_id,
            "nombre": db_user.rol.name
        }
    })
    refresh_token = create_refresh_token({"sub": db_user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token")
def refresh_token(payload: dict = Depends(validate_refresh_token), db: Session = Depends(get_db)):  # Cambiado a Session
    id = payload.get("sub")
    print("Id del usuario", id)
    if not id:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Traer usuario actualizado desde DB
    db_user = get_user_by_id(db, id)  # Quitado await
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Generar nuevo access token con toda la info
    new_access_token = create_access_token({
        "sub": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "name": db_user.name,
        "last_name": db_user.last_name,
        "sucursal": {
            "id": db_user.sucursal_id,
            "nombre": db_user.sucursal.nombre
        },
        "local": {
            "id": db_user.sucursal.local.id,
            "nombre": db_user.sucursal.local.name
        },
        "rol": {
            "id": db_user.rol_id,
            "nombre": db_user.rol.name
        }
    })

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/list/{sucursal_id}", response_model=List[dict])
def get_users(
    sucursal_id: str,
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)  # Cambiado a Session
):
    users = list_users(sucursal_id, db)  # Quitado await
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "name": u.name,
            "image": u.image,
            "is_active": u.is_active,
            "last_name": u.last_name,
            "rol": {"id": u.rol.id, "nombre": u.rol.name},
            "sucursal": {"id": u.sucursal.id, "nombre": u.sucursal.nombre}
        }
        for u in users
    ]

@router.patch("/update/{user_id}")
async def update_user_route(
    user_id: str,
    username: str = Form(...),
    email: str = Form(...),
    image: UploadFile = File(None),
    image_url: str = Form(None),
    name: str = Form(...),
    last_name: str = Form(...),
    sucursal_id: str = Form(...),
    rol_id: int = Form(...),
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)  # Cambiado a Session
):
    try:
        image_bytes = await image.read() if image else None  # Quitado await

        user = update_user(  # Quitado await
            db=db,
            user_id=user_id,
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            sucursal_id=sucursal_id,
            rol_id=rol_id,
            image_file=image_bytes,
            image_url=image_url
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
        return {
            "message": "Usuario actualizado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el usuario: {str(e)}"
        )

@router.delete("/delete/{user_id}")
def delete_user_route(
    user_id: str,
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)  # Cambiado a Session
):
    user = soft_delete_user(db, user_id)  # Quitado await

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    return {
        "message": "Usuario eliminado exitosamente"
    }

@router.get("/profile/{user_id}", response_model=UserOut)
def get_user_profile(
    user_id: str,
    current_user: dict = Depends(role_required("Administrador", "Dueño")),
    db: Session = Depends(get_db)  # Cambiado a Session
):
    if current_user["rol"]["nombre"] != "Administrador":
        raise HTTPException(status_code=403, detail="No tienes permiso")
    existing_user = get_profile(db, user_id)  # Quitado await
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    return existing_user

@router.patch("/profile/edit")
async def update_profile(
    username: str = Form(None),
    email: str = Form(None),
    image: UploadFile = File(None),
    image_url: str = Form(None),
    name: str = Form(None),
    last_name: str = Form(None),
    sucursal_id: str = Form(None),
    rol_id: int = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        
        image_bytes = await image.read() if image else None

        user = update_user(
            db=db,
            user_id=current_user["sub"],
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            sucursal_id=sucursal_id,
            rol_id=rol_id,
            image_file=image_bytes,
            image_url=image_url
        )

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")

        new_access_token = create_access_token({
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "last_name": user.last_name,
            "image": user.image,
            "is_active":user.is_active,
            "sucursal": {
                "id": user.sucursal_id,
                "nombre": user.sucursal.nombre
            },
            "local": {
                "id": user.sucursal.local.id,
                "nombre": user.sucursal.local.name
            },
            "rol": {
                "id": user.rol_id,
                "nombre": user.rol.name
            }
        })

        return {
            "message": "Perfil actualizado exitosamente",
            "access_token": new_access_token
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el perfil: {str(e)}"
        )