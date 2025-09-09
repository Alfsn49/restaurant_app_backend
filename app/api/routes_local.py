from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.local import LocalCreate, LocalUpdate, LocalOut
from app.core.database import SessionLocal
from app.crud.local import create_local, get_locals, get_local_by_name, get_local_by_id, soft_delete_local
from app.core.database import get_db

router = APIRouter(prefix="/locals", tags=["Locals"])

@router.get("/get-locals", response_model=list[LocalOut])
async def list_locals(db: AsyncSession = Depends(get_db)):
    locals = await get_locals(db)

    return await get_locals(db)

@router.post("/create-local", response_model=LocalOut, status_code=status.HTTP_201_CREATED)
async def create_new_local(name: str = Form(...),ruc: str = Form(...), direccion: str = Form(...), telefono: str = Form(...), image: UploadFile = File(None), db: AsyncSession = Depends(get_db)):
    try:
        # Leer la imagen solo si existe
        image_bytes = await image.read() if image else None

        existing_local = await get_local_by_name(db, name)

        if existing_local:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El local ya existe")
        
        return await create_local(db=db, name=name, ruc=ruc, direccion=direccion, telefono=telefono, image_file=image_bytes)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sucursal: {str(e)}"
        )
    
@router.get("/get-local/{local_id}", response_model=LocalOut)
async def get_local(local_id:str, db: AsyncSession = Depends(get_db)):
    local = await get_local_by_id(db, local_id)

    if not local:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Local not found")
    
    return local


@router.patch("/update-local/{local_id}", response_model=LocalOut)
async def update_local(local_id:str, local_data: LocalUpdate, db: AsyncSession = Depends(get_db)):
    local = await update_local( local_id, local_data,db)
    if not local:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encuentra el local")
    
    return local

@router.delete("/delete-local/{local_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_local(local_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await soft_delete_local(db, local_id)

    if not deleted:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Local no encontrado o ya eliminado")
    
    return 