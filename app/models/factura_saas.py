from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from app.core.database import Base
from datetime import datetime
from cuid2 import cuid_wrapper

# Usamos la función generadora
cuid_generator = cuid_wrapper()

class FacturaSaas(Base):
    __tablename__ = "factura_saas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    fecha_emision: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    numero_factura: Mapped[str] = mapped_column(String(50))
    forma_pago: Mapped[str] = mapped_column(String(50), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    iva: Mapped[float] = mapped_column(Float, nullable=False)
    estado_autorizacion: Mapped[str] = mapped_column(String(50), nullable=False)
    clave_acceso: Mapped[str] = mapped_column(String(50), nullable=False)
    firma_electronica: Mapped[str] = mapped_column(Text, nullable=False)
    codigo_qr: Mapped[str] = mapped_column(Text, nullable=False)

    local_id: Mapped[str] = mapped_column(ForeignKey("locales.id"))
    local: Mapped["Local"] = relationship("Local",back_populates="facturas_saas")

    plan_id: Mapped[str] = mapped_column(ForeignKey("planes.id"))
    plan: Mapped["Plan"] = relationship("Plan",back_populates="facturas_saas")
    


from app.models.local import Local
from app.models.plan import Plan

