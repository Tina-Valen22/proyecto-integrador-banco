from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Reporte(SQLModel, table=True):
    idReporte: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.now)

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.idUsuario")
    credito_id: Optional[int] = Field(default=None, foreign_key="credito.idCredito")
    simulacion_id: Optional[int] = Field(default=None, foreign_key="simulacion.idSimulacion")