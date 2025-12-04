from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.credito_categoria import CreditoCategoria

class Credito(SQLModel, table=True):
    idCredito: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    plazo: int
    tipo: str
    descripcion: Optional[str] = None

    usuario_id: int = Field(foreign_key="usuario.idUsuario")

    # Relaciones
    usuario: Optional["Usuario"] = Relationship(back_populates="creditos")
    interes: Optional["Interes"] = Relationship(back_populates="credito")
    categorias: List["Categoria"] = Relationship(
        back_populates="creditos",
        link_model=CreditoCategoria
    )