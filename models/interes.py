from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Interes(SQLModel, table=True):
    idInteres: Optional[int] = Field(default=None, primary_key=True)
    tasa: float
    tipo: str

    credito_id: int = Field(foreign_key="credito.idCredito")
    credito: Optional["Credito"] = Relationship(back_populates="interes")

    simulaciones: List["Simulacion"] = Relationship(back_populates="interes")
