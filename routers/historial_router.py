from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database import engine
from models.historial import Historial
from models.usuario import Usuario

router = APIRouter(prefix="/historial", tags=["Historial"])

@router.get("/")
def listar_historial():
    with Session(engine) as session:
        return session.exec(select(Historial)).all()

@router.post("/restaurar_usuario/")
def restaurar_usuario(nombre: str, ingresos: float, gastos: float):
    with Session(engine) as session:
        nuevo_usuario = Usuario(nombre=nombre, ingresos=ingresos, gastos=gastos)
        session.add(nuevo_usuario)
        session.commit()
        session.refresh(nuevo_usuario)

        nuevo_historial = Historial(
            entidad="Usuario",
            accion="RESTAURAR",
            descripcion=f"Usuario '{nombre}' restaurado desde historial"
        )
        session.add(nuevo_historial)
        session.commit()
        return {"mensaje": f"Usuario '{nombre}' restaurado exitosamente"}
