from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime
from app.core.database import Base
from datetime import datetime



class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    usuarios: Mapped[list["User"]] = relationship("User", back_populates="rol")

from app.models.user import User