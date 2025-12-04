from __future__ import annotations

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Interes(SQLModel, table=True):
    idInteres: Optional[int] = Field(default=None, primary_key=True)
    tasa: float
    tipo: str

    # 🔴 Antes: foreign_key="credito.id"
    # ✅ Ahora: foreign_key="credito.idCredito"
    credito_id: int = Field(foreign_key="credito.idCredito")

    credito: Optional["Credito"] = Relationship(back_populates="interes")
    simulaciones: List["Simulacion"] = Relationship(back_populates="interes")