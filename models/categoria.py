from __future__ import annotations

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from .credito_categoria import CreditoCategoria


class Categoria(SQLModel, table=True):
    idCategoria: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None

    # Relación N:M con Credito a través de CreditoCategoria
    creditos: List["Credito"] = Relationship(
        back_populates="categorias",
        link_model=CreditoCategoria,
    )