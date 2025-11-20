from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models.reporte import Reporte
from models.historial import Historial
from datetime import datetime

router = APIRouter(prefix="/reportes", tags=["Reportes"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/")
def crear_reporte(reporte: Reporte, session: Session = Depends(get_session)):
    session.add(reporte)
    session.commit()
    session.refresh(reporte)
    return reporte

@router.get("/")
def listar_reportes(session: Session = Depends(get_session)):
    return session.exec(select(Reporte)).all()

@router.get("/{reporte_id}")
def obtener_reporte(reporte_id: int, session: Session = Depends(get_session)):
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return reporte

@router.put("/{reporte_id}")
def actualizar_reporte(reporte_id: int, datos: Reporte, session: Session = Depends(get_session)):
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    reporte.grafico = datos.grafico
    reporte.estadisticas = datos.estadisticas
    session.commit()
    session.refresh(reporte)
    return reporte

@router.delete("/{reporte_id}")
def eliminar_reporte(reporte_id: int, session: Session = Depends(get_session)):
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    historial = Historial(
        entidad="Reporte",
        accion="ELIMINAR",
        descripcion=f"Reporte {reporte.idReporte} eliminado",
        fecha=datetime.now()
    )
    session.add(historial)
    session.delete(reporte)
    session.commit()
    return {"mensaje": "Reporte eliminado y registrado en historial"}
