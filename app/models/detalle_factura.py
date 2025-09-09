from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from app.core.database import Base
from cuid2 import cuid_wrapper


# Usamos la función generadora
cuid_generator = cuid_wrapper()

class DetalleFactura(Base):

    __tablename__ = "detalle_factura"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)

    factura_id: Mapped[str] = mapped_column(ForeignKey("facturas.id"))
    factura: Mapped["Factura"] = relationship(back_populates="detalle_factura")

    producto_variante_id: Mapped[str] = mapped_column(ForeignKey("producto_variantes.id"))
    producto_variantes: Mapped["Producto_Variante"] = relationship("Producto_Variante", back_populates="detalle_factura")

from app.models.factura import Factura
from app.models.producto_variante import Producto_Variante
