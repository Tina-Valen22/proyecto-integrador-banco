from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Simulacion(SQLModel, table=True):
    idSimulacion: Optional[int] = Field(default=None, primary_key=True)
    cuotaMensual: float
    interesTotal: float
    saldoFinal: float

    # Relación con Interes
    interes_id: int = Field(foreign_key="interes.idInteres")

    interes: Optional["Interes"] = Relationship(back_populates="simulaciones")