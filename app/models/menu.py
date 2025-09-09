from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base



class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    horario: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"] = relationship("Sucursal", back_populates="menus")

    producto_variantes: Mapped[list["Producto_Variante"]] = relationship(
        "Producto_Variante", back_populates="menu"
    )

from app.models.sucursal import Sucursal
from app.models.producto_variante import Producto_Variante