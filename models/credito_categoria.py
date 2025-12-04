from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field


class CreditoCategoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    credito_id: int = Field(foreign_key="credito.idCredito")
    categoria_id: int = Field(foreign_key="categoria.idCategoria")