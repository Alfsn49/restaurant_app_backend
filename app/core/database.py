from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import ssl

# Configuración SSL para conexiones seguras
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Para Neon, usa el formato estándar de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'),
    echo=True,  # Para ver las queries en consola
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,  # IMPORTANTE: Verificar que la conexión esté activa
    connect_args={
        "sslmode": "require",
        "sslrootcert": ssl_context
    }
)

# Para el desarrollo
# engine = create_engine(
#     settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'),
#     echo=True,  # Para ver las queries en consola
#     pool_size=5,
#     max_overflow=10,
#     pool_timeout=30,
#     pool_recycle=1800
# )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()