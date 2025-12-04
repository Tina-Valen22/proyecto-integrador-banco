# models/usuario.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Usuario(SQLModel, table=True):
    idUsuario: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    ingresos: float
    gastos: float
    correo: str
    telefono: str

    # NUEVO CAMPO para almacenar la ruta del archivo de cédula
    cedula: Optional[str] = Field(
        default=None,
        description="Ruta del archivo de cédula (PDF o JPG) almacenado en el servidor",
    )