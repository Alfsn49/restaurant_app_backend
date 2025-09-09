from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper



cuid_generator = cuid_wrapper()

class Product(Base):
    __tablename__ = "productos"

    id:Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    nombre: Mapped[str] =mapped_column(String(150), nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)

    sucursal_id: Mapped[str] = mapped_column(ForeignKey("sucursales.id"))
    sucursal: Mapped["Sucursal"]= relationship("Sucursal", back_populates="productos")

    categoria_id: Mapped[int]=mapped_column(ForeignKey("categorias.id"))
    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="productos")

    variantes: Mapped[list["Producto_Variante"]] = relationship("Producto_Variante", back_populates="producto")

from app.models.categoria import Categoria
from app.models.producto_variante import Producto_Variante
from app.models.sucursal import Sucursal