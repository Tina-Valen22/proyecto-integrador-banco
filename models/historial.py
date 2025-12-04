from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Historial(SQLModel, table=True):
    idHistorial: Optional[int] = Field(default=None, primary_key=True)
    entidad: str
    accion: str
    descripcion: str
    fecha: datetime