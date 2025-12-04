from __future__ import annotations

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Usuario(SQLModel, table=True):
    idUsuario: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    ingresos: float
    gastos: float
    correo: Optional[str] = None
    telefono: Optional[str] = None

    # Relación 1:N con Credito
    creditos: List["Credito"] = Relationship(back_populates="usuario")