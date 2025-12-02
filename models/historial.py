from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Historial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    accion: str
    detalle: str

    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: Optional["Usuario"] = Relationship(back_populates="historial")
