from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Quitar sslmode de la URL para asyncpg
url = settings.DATABASE_URL.replace("?sslmode=require&channel_binding=require", "")

engine = create_async_engine(url, echo=True,
                             connect_args={"ssl": True}  
                             )
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session
