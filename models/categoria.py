from typing import Optional
from sqlmodel import SQLModel, Field


class Categoria(SQLModel, table=True):
    idCategoria: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None