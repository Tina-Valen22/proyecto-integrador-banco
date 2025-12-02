from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Simulacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cuota_mensual: float
    interes_total: float
    saldo_final: float

    interes_id: int = Field(foreign_key="interes.id")
    interes: Optional["Interes"] = Relationship(back_populates="simulaciones")
    reportes: List["Reporte"] = Relationship(back_populates="simulacion")
