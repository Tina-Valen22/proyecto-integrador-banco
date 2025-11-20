from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Simulacion(SQLModel, table=True):
    idSimulacion: Optional[int] = Field(default=None, primary_key=True)
    cuotaMensual: float
    interesTotal: float
    saldoFinal: float

    interes_id: int = Field(foreign_key="interes.idInteres")
    interes: Optional["Interes"] = Relationship(back_populates="simulaciones")

    reportes: List["Reporte"] = Relationship(back_populates="simulacion")
