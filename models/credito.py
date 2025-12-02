from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Credito(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    plazo: int
    tipo: str
    usuario_id: int = Field(foreign_key="usuario.id")

    usuario: Optional["Usuario"] = Relationship(back_populates="creditos")
    intereses: List["Interes"] = Relationship(back_populates="credito")
    categorias: List["CreditoCategoria"] = Relationship(back_populates="credito")
