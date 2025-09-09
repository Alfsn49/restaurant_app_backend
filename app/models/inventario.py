from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper


cuid_generator = cuid_wrapper()

class Inventario(Base):
    __tablename__ = "inventarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    cantidad: Mapped[int] = mapped_column(Integer)

    producto_variante_id: Mapped[int] = mapped_column(ForeignKey("producto_variantes.id"))
    producto_variantes: Mapped["Producto_Variante"] = relationship("Producto_Variante", back_populates="inventario")

    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"]= relationship("Sucursal", back_populates="inventario")

from app.models.producto_variante import Producto_Variante
from app.models.sucursal import Sucursal