from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Float
from app.core.database import Base
from datetime import datetime
from cuid2 import cuid_wrapper
cuid_generator = cuid_wrapper()

class Orden(Base):
    __tablename__= "ordenes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)

    numero_orden: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[DateTime] = mapped_column(DateTime,default=datetime.now)
    estado: Mapped[str] = mapped_column(String, nullable=True)
    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"] = relationship("Sucursal", back_populates="ordenes")

    detalles_orden: Mapped[list["OrdenDetalle"]] = relationship("OrdenDetalle")

from app.models.sucursal import Sucursal

class OrdenDetalle(Base):
    __tablename__ = "ordenes_detalle"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    orden_id: Mapped[str] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    producto_variante_id: Mapped[str] = mapped_column(ForeignKey("producto_variantes.id"))

    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float,nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    orden: Mapped["Orden"]= relationship("Orden", back_populates="detalles_orden")
    producto_variantes: Mapped["Producto_Variante"]= relationship("Producto_Variante")

    from app.models.producto_variante import Producto_Variante



