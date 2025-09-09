from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base

from cuid2 import cuid_wrapper



# Usamos la función generadora
cuid_generator = cuid_wrapper()

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    sucursal_id: Mapped[str]=mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"] = relationship("Sucursal", back_populates="usuarios")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
    rol_id: Mapped[int]= mapped_column(ForeignKey("roles.id"))
    rol: Mapped["Rol"] = relationship("Rol", back_populates="usuarios")

    suscripciones: Mapped[list["Suscripcion"]] = relationship("Suscripcion", back_populates="user")
    facturas: Mapped[list["Factura"]] = relationship("Factura", back_populates="user")

from app.models.rol import Rol
from app.models.suscripcion import Suscripcion
from app.models.factura import Factura
from app.models.sucursal import Sucursal