from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Usuario(SQLModel, table=True):
    idUsuario: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    ingresos: float
    gastos: float

    creditos: List["Credito"] = Relationship(back_populates="usuario")
