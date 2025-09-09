from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from app.core.database import Base
from datetime import datetime
from cuid2 import cuid_wrapper



cuid_generator = cuid_wrapper()

class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    numero_factura: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    fecha_emision: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    forma_pago: Mapped[str] = mapped_column(String(50), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    iva: Mapped[float] = mapped_column(Float, nullable=False)
    estado_autorizacion: Mapped[str] = mapped_column(String(50), nullable=False)
    clave_acceso: Mapped[str] = mapped_column(String(50), nullable=False)
    firma_electronica: Mapped[str] = mapped_column(Text, nullable=False)
    codigo_qr: Mapped[str] = mapped_column(Text, nullable=False)
    emisor_ruc: Mapped[str] = mapped_column(String(13), nullable=False)

    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"] = relationship("Sucursal",back_populates="facturas")

    cliente_id: Mapped[str] = mapped_column(ForeignKey("clientes.id"))
    cliente: Mapped["Cliente"] = relationship("Cliente",back_populates="facturas")

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User",back_populates="facturas")

    detalle_factura: Mapped[list["DetalleFactura"]] = relationship("DetalleFactura", back_populates="factura")

from app.models.sucursal import Sucursal
from app.models.cliente import Cliente
from app.models.user import User
from app.models.detalle_factura import DetalleFactura