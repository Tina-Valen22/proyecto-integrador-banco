# routers/historial_router.py
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database import engine
from models.historial import Historial
from models.usuario import Usuario
from datetime import datetime

router = APIRouter(prefix="/historial", tags=["Historial"])

@router.get("/")
def listar_historial():
    with Session(engine) as session:
        return session.exec(select(Historial)).all()

@router.post("/restaurar_usuario/")
def restaurar_usuario(nombre: str, ingresos: float, gastos: float):
    with Session(engine) as session:
        nuevo = Usuario(nombre=nombre, ingresos=ingresos, gastos=gastos)
        session.add(nuevo)
        session.commit()
        session.refresh(nuevo)

        h = Historial(entidad="Usuario", accion="RESTAURAR",
                      descripcion=f"Usuario '{nombre}' restaurado", fecha=datetime.now())
        session.add(h)
        session.commit()
        return {"mensaje": f"Usuario '{nombre}' restaurado exitosamente"}
