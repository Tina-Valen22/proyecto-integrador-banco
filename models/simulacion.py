from typing import Optional
from sqlmodel import SQLModel, Field


class Simulacion(SQLModel, table=True):
    idSimulacion: Optional[int] = Field(default=None, primary_key=True)
    cuotaMensual: float
    interesTotal: float
    saldoFinal: float

    interes_id: int = Field(foreign_key="interes.idInteres")