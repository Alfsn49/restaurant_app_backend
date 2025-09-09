from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper



cuid_generator = cuid_wrapper()

class Local(Base):
    __tablename__ = "locales"

    id: Mapped[str] = mapped_column(String, primary_key=True, default= cuid_generator)
    name: Mapped[str] = mapped_column(String(150))
    ruc: Mapped[str] = mapped_column(String(13), unique=True, index=True)
    direccion: Mapped[str]= mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sucursales: Mapped[list["Sucursal"]] = relationship("Sucursal", back_populates="local")
    
    #locales: Mapped[list["Cliente"]] = relationship("Cliente", back_populates="sucursal")

    suscripciones: Mapped[list["Suscripcion"]]= relationship("Suscripcion", back_populates="local")

    facturas_saas: Mapped[list["FacturaSaas"]] = relationship("FacturaSaas", back_populates="local")


from app.models.sucursal import Sucursal
#from app.models.local import Local
from app.models.suscripcion import Suscripcion
from app.models.factura_saas import FacturaSaas