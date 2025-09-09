import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("Database_neontech")
    DATABASE_SUPABASE: str = os.getenv("Database_neontech")  # remoto sync
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecreto")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()