from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper



cuid_generator = cuid_wrapper()

class Sucursal(Base):
    __tablename__ = "sucursales"

    id: Mapped[str] = mapped_column(String, primary_key=True, default = cuid_generator)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    ruc: Mapped[str] = mapped_column(String(13), unique=True, index=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    local_id : Mapped[str] = mapped_column(ForeignKey("locales.id"))

    local:Mapped["Local"] = relationship("Local",back_populates="sucursales")

    zonas: Mapped[list["Zona"]] = relationship("Zona", back_populates="sucursal")

    clientes: Mapped[list["Cliente"]] = relationship("Cliente", back_populates="sucursal")

    facturas: Mapped[list["Factura"]] = relationship("Factura", back_populates="sucursal")

    inventario: Mapped[list["Inventario"]] = relationship("Inventario", back_populates="sucursal")

    menus: Mapped[list["Menu"]] = relationship("Menu", back_populates="sucursal")

    productos: Mapped[list["Product"]] = relationship("Product",back_populates="sucursal")

    usuarios : Mapped[list["User"]] = relationship("User", back_populates="sucursal")

    ordenes: Mapped[list["Orden"]] = relationship("Orden", back_populates="sucursal")


from app.models.local import Local
from app.models.zona import Zona
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.models.inventario import Inventario
from app.models.menu import Menu
from app.models.product import Product
from app.models.user import User
from app.models.orden import Orden