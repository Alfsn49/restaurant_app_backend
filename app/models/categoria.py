from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    productos: Mapped[list["Product"]] = relationship("Product", back_populates="categoria")

from app.models.product import Product