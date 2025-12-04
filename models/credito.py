from typing import Optional
from sqlmodel import SQLModel, Field


class Credito(SQLModel, table=True):
    idCredito: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    plazo: int
    tipo: str
    descripcion: Optional[str] = None

    usuario_id: int = Field(foreign_key="usuario.idUsuario")