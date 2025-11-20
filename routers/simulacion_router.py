from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models.simulacion import Simulacion
from models.historial import Historial
from datetime import datetime

router = APIRouter(prefix="/simulaciones", tags=["Simulaciones"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/")
def crear_simulacion(simulacion: Simulacion, session: Session = Depends(get_session)):
    session.add(simulacion)
    session.commit()
    session.refresh(simulacion)
    return simulacion

@router.get("/")
def listar_simulaciones(session: Session = Depends(get_session)):
    return session.exec(select(Simulacion)).all()

@router.get("/{simulacion_id}")
def obtener_simulacion(simulacion_id: int, session: Session = Depends(get_session)):
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return simulacion

@router.put("/{simulacion_id}")
def actualizar_simulacion(simulacion_id: int, datos: Simulacion, session: Session = Depends(get_session)):
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    simulacion.cuotaMensual = datos.cuotaMensual
    simulacion.interesTotal = datos.interesTotal
    simulacion.saldoFinal = datos.saldoFinal
    session.commit()
    session.refresh(simulacion)
    return simulacion

@router.delete("/{simulacion_id}")
def eliminar_simulacion(simulacion_id: int, session: Session = Depends(get_session)):
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    historial = Historial(
        entidad="Simulación",
        accion="ELIMINAR",
        descripcion=f"Simulación {simulacion.idSimulacion} eliminada",
        fecha=datetime.now()
    )
    session.add(historial)
    session.delete(simulacion)
    session.commit()
    return {"mensaje": "Simulación eliminada y registrada en historial"}
