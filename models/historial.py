from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Historial(SQLModel, table=True):
    idHistorial: Optional[int] = Field(default=None, primary_key=True)
    entidad: str
    accion: str
    descripcion: str
    fecha: datetime = Field(default_factory=datetime.now)
