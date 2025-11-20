from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.credito_categoria import CreditoCategoria

class Categoria(SQLModel, table=True):
    idCategoria: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

    creditos: List["Credito"] = Relationship(
        back_populates="categorias",
        link_model=CreditoCategoria
    )
