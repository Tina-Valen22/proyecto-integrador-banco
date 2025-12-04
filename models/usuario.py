from typing import Optional
from sqlmodel import SQLModel, Field


class Usuario(SQLModel, table=True):
    idUsuario: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    ingresos: float
    gastos: float
    correo: Optional[str] = None
    telefono: Optional[str] = None