from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Historial(SQLModel, table=True):
    idHistorial: Optional[int] = Field(default=None, primary_key=True)
    entidad: str
    accion: str
    descripcion: str
    fecha: datetime