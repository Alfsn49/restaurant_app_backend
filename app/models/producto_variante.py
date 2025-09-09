from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Float
from app.core.database import Base



class Producto_Variante(Base):
    __tablename__ = "producto_variantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200))
    precio: Mapped[float] = mapped_column(Float)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    image: Mapped[str] = mapped_column(String, nullable=True)

    producto_id: Mapped[str] = mapped_column(ForeignKey("productos.id"))
    producto: Mapped["Product"] = relationship("Product", back_populates="variantes")

    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"))
    menu: Mapped["Menu"] = relationship("Menu", back_populates="producto_variantes")

    zona_id: Mapped[int] = mapped_column(ForeignKey("zonas.id"), nullable=True)
    zona: Mapped["Zona"] = relationship("Zona", back_populates="producto_variantes")

    detalle_factura: Mapped[list["DetalleFactura"]] = relationship("DetalleFactura", back_populates="producto_variantes")

    inventario: Mapped[list["Inventario"]] = relationship("Inventario", back_populates="producto_variantes")

    detalles_orden: Mapped[list["OrdenDetalle"]] = relationship("OrdenDetalle", back_populates="producto_variantes")


from app.models.product import Product
from app.models.menu import Menu
from app.models.zona import Zona
from app.models.detalle_factura import DetalleFactura
from app.models.inventario import Inventario
from app.models.orden import OrdenDetalle