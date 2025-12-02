from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Interes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tasa: float
    tipo: str
    credito_id: int = Field(foreign_key="credito.id")

    credito: Optional["Credito"] = Relationship(back_populates="intereses")
    simulaciones: List["Simulacion"] = Relationship(back_populates="interes")
