from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session  # Cambiado de AsyncSession a Session
from app.schemas.local import LocalCreate, LocalUpdate, LocalOut
from app.core.database import get_db
from app.crud.local import create_local, get_locals, get_local_by_name, get_local_by_id, soft_delete_local, update_local  # Añadido update_local al import

router = APIRouter(prefix="/locals", tags=["Locals"])

@router.get("/get-locals", response_model=list[LocalOut])
def list_locals(db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    locals = get_locals(db)  # Quitado await
    return locals  # Corregido: retornar la variable ya obtenida

@router.post("/create-local", response_model=LocalOut, status_code=status.HTTP_201_CREATED)
async def create_new_local(
    name: str = Form(...),
    ruc: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)  # Quitado async, cambiado a Session
):
    try:
        # Leer la imagen solo si existe
        image_bytes = await image.read() if image else None  # Quitado await
        

        existing_local = get_local_by_name(db, name)  # Quitado await

        if existing_local:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El local ya existe")
        
        return create_local(db=db, name=name, ruc=ruc, direccion=direccion, telefono=telefono, image_file=image_bytes)  # Quitado await

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating local: {str(e)}"  # Corregido el mensaje de error
        )
    
@router.get("/get-local/{local_id}", response_model=LocalOut)
def get_local(local_id: str, db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    local = get_local_by_id(db, local_id)  # Quitado await

    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local not found"
        )
    
    return local

@router.patch("/update-local/{local_id}", response_model=LocalOut)
def update_local_route(local_id: str, local_data: LocalUpdate, db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    local = update_local(local_id, local_data, db)  # Quitado await y corregido el orden de parámetros
    if not local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encuentra el local"
        )
    
    return local

@router.delete("/delete-local/{local_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_local(local_id: str, db: Session = Depends(get_db)):  # Quitado async, cambiado a Session
    deleted = soft_delete_local(db, local_id)  # Quitado await

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local no encontrado o ya eliminado"
        )
    
    return  # Para status 204 NO CONTENT