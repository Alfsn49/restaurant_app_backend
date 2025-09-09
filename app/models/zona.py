from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base



class Zona(Base):
    __tablename__ = "zonas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))

    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"]= relationship(back_populates="zonas")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    producto_variantes: Mapped[list["Producto_Variante"]] = relationship("Producto_Variante", back_populates="zona")

from app.models.sucursal import Sucursal
from app.models.producto_variante import Producto_Variante