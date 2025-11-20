from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Reporte(SQLModel, table=True):
    idReporte: Optional[int] = Field(default=None, primary_key=True)
    grafico: str
    estadisticas: str

    simulacion_id: int = Field(foreign_key="simulacion.idSimulacion")
    simulacion: Optional["Simulacion"] = Relationship(back_populates="reportes")
