from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class CreditoCategoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    credito_id: int = Field(foreign_key="credito.id")
    categoria_id: int = Field(foreign_key="categoria.id")

    credito: Optional["Credito"] = Relationship(back_populates="categorias")
    categoria: Optional["Categoria"] = Relationship(back_populates="creditos")
