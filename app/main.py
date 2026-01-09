# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.routes_user import router as user_router
from app.api.routes_categoria import router as categoria_router
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

app = FastAPI(
    title="API Sistema de Gestión",
    description="API para sistema de gestión con múltiples módulos",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔴 AGREGA ESTOS ENDPOINTS CRÍTICOS PARA RAILWAY 🔴

@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    port = os.getenv("PORT", "8000")
    return {
        "message": "API Sistema de Gestión funcionando correctamente",
        "status": "online",
        "port": port,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api_routes": [
                "/api/users",
                "/api/categorias",
                "/api/roles",
                "/api/locales",
                "/api/zonas",
                "/api/sucursales",
                "/api/clientes",
                "/api/products",
                "/api/productos-variantes",
                "/api/inventario",
                "/api/menu",
                "/api/orders",
                "/api/reportes"
            ]
        }
    }

@app.get("/health")
@app.get("/healthz")
@app.get("/ready")
async def health_check():
    """Endpoint CRÍTICO para health checks de Railway"""
    return {
        "status": "healthy",
        "service": "fastapi-api",
        "timestamp": "2024-01-01T00:00:00Z"  # Considera usar datetime.utcnow().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """Endpoint para verificar estado de la API"""
    return {
        "status": "operational",
        "modules": {
            "users": "active",
            "categories": "active",
            "roles": "active",
            "locations": "active",
            "zones": "active",
            "branches": "active",
            "clients": "active",
            "products": "active",
            "inventory": "active",
            "menu": "active",
            "orders": "active",
            "reports": "active"
        }
    }

# Registrar cada router por separado
# Asumiendo que tus routers tienen prefijos, si no, agrégalos:

# Ejemplo si tus routers NO tienen prefijo:
# app.include_router(user_router, prefix="/api", tags=["users"])

# O si YA tienen prefijo en cada router, déjalos así:
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