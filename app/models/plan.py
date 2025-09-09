from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base
from cuid2 import cuid_wrapper


# Usamos la función generadora
cuid_generator = cuid_wrapper()

class Plan(Base):
    __tablename__ = "planes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    duracion_mes: Mapped[int] = mapped_column(Integer, nullable=False)

    suscripciones: Mapped[list["Suscripcion"]]= relationship("Suscripcion", back_populates="plan")
    
    facturas_saas: Mapped[list["FacturaSaas"]] = relationship("FacturaSaas", back_populates="plan")

from app.models.suscripcion import Suscripcion
from app.models.factura_saas import FacturaSaas