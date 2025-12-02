from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Credito(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    descripcion: str
    usuario_id: int = Field(foreign_key="usuario.id")

    usuario: Optional["Usuario"] = Relationship(back_populates="creditos")
