from sqlmodel import SQLModel, Field
from typing import Optional

class Historial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    accion: str
    detalle: str
