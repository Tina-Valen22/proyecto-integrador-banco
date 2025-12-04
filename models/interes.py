from typing import Optional
from sqlmodel import SQLModel, Field


class Interes(SQLModel, table=True):
    idInteres: Optional[int] = Field(default=None, primary_key=True)
    tasa: float
    tipo: str

    credito_id: int = Field(foreign_key="credito.idCredito")