from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base
from cuid2 import cuid_wrapper



# Usamos la función generadora
cuid_generator = cuid_wrapper()

class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid_generator)
    fecha_inicio: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    pagado: Mapped[bool] = mapped_column(Boolean, default=False)

    local_id: Mapped[str] = mapped_column(ForeignKey("locales.id"))
    plan_id: Mapped[str] = mapped_column(ForeignKey("planes.id"))
    usuario_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    local: Mapped["Local"] = relationship("Local", back_populates="suscripciones")
    plan: Mapped["Plan"]= relationship("Plan", back_populates="suscripciones")
    user: Mapped["User"]= relationship("User", back_populates="suscripciones")

from app.models.local import Local
from app.models.plan import Plan
from app.models.user import User