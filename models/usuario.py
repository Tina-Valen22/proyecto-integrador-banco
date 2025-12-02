from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    correo: str
    telefono: str

    creditos: List["Credito"] = Relationship(back_populates="usuario")
