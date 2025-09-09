from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper


cuid_generator = cuid_wrapper()

class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    nombre: Mapped[str] = mapped_column(String(250))
    ruc_cedula: Mapped[str] = mapped_column(String(13))
    direccion: Mapped[str] = mapped_column(String(255))
    telefono: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(150))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"] = relationship(back_populates="clientes")
    
    #local_id: Mapped[str] = mapped_column(ForeignKey("locales.id"))
    #local: Mapped["Local"] = relationship(back_populates="locales")

    facturas: Mapped[list["Factura"]] = relationship("Factura", back_populates="cliente")

from app.models.sucursal import Sucursal
#from app.models.local import Local
from app.models.factura import Factura