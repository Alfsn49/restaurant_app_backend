from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.menu import MenuOut, MenuCreate, MenuUpdate, MenuOutSimple
from app.crud.menu import (
    create_menu as crud_create_menu,
    get_menu_by_id as crud_get_menu_by_id,
    get_menus as crud_get_menus,
    update_menu as crud_update_menu,
    soft_delete_menu as crud_soft_delete_menu,
    get_menus_by_sucursal as crud_get_menus_by_sucursal,
)

router = APIRouter(prefix="/menus", tags=["Menus"])


# 📌 Crear un menú
@router.post("/create", response_model=MenuOutSimple, status_code=status.HTTP_201_CREATED)
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    new_menu = crud_create_menu(db, menu)
    if not new_menu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un menú con este nombre y horario en la sucursal."
        )
    return new_menu


# 📌 Obtener menús por sucursal
@router.get("/get-menus-by-sucursal/{sucursal_id}", response_model=list[MenuOutSimple])
def list_menus_by_sucursal(sucursal_id: str, db: Session = Depends(get_db)):
    result = crud_get_menus_by_sucursal(db, sucursal_id)
    return result


# 📌 Obtener todos los menús
@router.get("/list", response_model=list[MenuOut])
def get_menus(db: Session = Depends(get_db)):
    menus = crud_get_menus(db)
    return menus


# 📌 Obtener menú por ID
@router.get("/{menu_id}", response_model=MenuOut)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    menu = crud_get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menú no encontrado")
    return menu


# 📌 Actualizar menú
@router.put("/{menu_id}", response_model=MenuOut)
def update_menu(menu_id: str, menu_data: MenuUpdate, db: Session = Depends(get_db)):
    updated_menu = crud_update_menu(db, menu_data, menu_id)
    if not updated_menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menú no encontrado")
    return updated_menu


# 📌 Eliminar menú
@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(menu_id: str, db: Session = Depends(get_db)):
    result = crud_soft_delete_menu(db, menu_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menú no encontrado")
    return {"detail": "Menú eliminado correctamente"}
