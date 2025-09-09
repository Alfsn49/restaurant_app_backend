# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_user import router as user_router
from app.api.routes_categoria import router as categoria_router  # otro router
from app.api.routes_rol import router as rol_router
from app.api.routes_local import router as local_router
from app.api.routes_zona import router as zona_router
from app.api.routes_sucursal import router as sucursal_router
from app.api.routes_cliente import router as cliente_router
from app.api.routes_product import router as product_router
from app.api.routes_producto_variante import router as producto_variante_router
from app.api.routes_inventario import router as inventario_router
from app.api.routes_menu import router as menu_router
from app.api.routes_order import router as order_router
from app.api.routes_reportes import router as reportes_router

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Aquí puedes poner ["http://localhost:3000"] si solo es para un frontend específico
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos: GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Permite todos los headers
)

# Registrar cada router por separado
app.include_router(user_router)
app.include_router(categoria_router)
app.include_router(rol_router)
app.include_router(local_router)
app.include_router(zona_router)
app.include_router(sucursal_router)
app.include_router(cliente_router)
app.include_router(product_router)
app.include_router(producto_variante_router)
app.include_router(inventario_router)
app.include_router(menu_router)
app.include_router(order_router)
app.include_router(reportes_router)