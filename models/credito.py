from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from typing import List

class Credito(SQLModel, table=True):
    idCredito: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    plazo: int
    tipo: str

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.idUsuario")
    usuario: Optional["Usuario"] = Relationship(back_populates="creditos")

    interes: Optional["Interes"] = Relationship(back_populates="credito")
