from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.crud.cliente import create_Cliente, get_cliente_by_DNI, get_cliente_by_id, get_clients ,update_cliente, soft_delete_cliente, ClienteExistenteError

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/get-clientes", response_model=list[ClienteOut])
async def list_clientes(db: AsyncSession = Depends(get_db)):
    clientes = await get_clients(db)

    return await clientes

@router.get("/get-cliente/{dni}", response_model=ClienteOut)
async def get_cliente_dni(dni:str, db: AsyncSession = Depends(get_db)):
    cliente = await get_cliente_by_DNI(db, dni)

    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encuentra un cliente")

    return cliente

@router.post("/create-cliente", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
async def create_clientes(cliente_data:ClienteCreate, db: AsyncSession = Depends(get_db)):
    try:
        cliente = await create_Cliente(db, cliente_data)
        return cliente
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except ClienteExistenteError as cee:
        raise HTTPException(status_code=400, detail=str(cee))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    

@router.patch("/update-cliente/{cliente_id}", response_model=ClienteOut)
async def update_clientes(cliente_id:str, cliente_data:ClienteUpdate, db: AsyncSession = Depends(get_db)):
    try:
        cliente_actualizado = await update_cliente(db, cliente_id, cliente_data)
        return cliente_actualizado
    except HTTPException:
        # Se relanza para que FastAPI maneje la respuesta HTTP
        raise
    except Exception as e:
        # Aquí puedes loguear el error si quieres
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/delete_cliente/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(cliente_id:str,sucursal_id: str = Query(..., description="ID de la sucursal"), db: AsyncSession= Depends(get_db)):
    deleted = await soft_delete_cliente(db, cliente_id)

    if not deleted:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado o ya eliminado")
    
    return