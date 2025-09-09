from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL_SYNC = settings.DATABASE_SUPABASE.replace("+asyncpg", "")

engine_sync = create_engine(DATABASE_URL_SYNC, echo=True)
SessionLocalSync = sessionmaker(bind=engine_sync, expire_on_commit=False)
BaseSync = declarative_base()