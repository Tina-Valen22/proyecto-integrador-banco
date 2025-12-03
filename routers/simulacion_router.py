# routers/simulacion_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from models.simulacion import Simulacion
from models.interes import Interes
from models.historial import Historial
from typing import List
from datetime import datetime

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/simulaciones", tags=["Simulaciones"])

@router.get("/")
def ver_simulaciones(request: Request, session: Session = Depends(get_session)):
    sims = session.exec(select(Simulacion)).all()
    return templates.TemplateResponse("simulaciones.html", {"request": request, "simulaciones": sims})

@router.post("/crear")
def crear_simulacion(cuota_mensual: float = Form(...), interes_total: float = Form(...), saldo_final: float = Form(...), interes_id: int = Form(...), session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    sim = Simulacion(cuota_mensual=cuota_mensual, interes_total=interes_total, saldo_final=saldo_final, interes_id=interes_id)
    session.add(sim)
    session.commit()
    session.refresh(sim)

    # registrar en historial, link al usuario via interés->credito->usuario
    usuario_id = None
    try:
        usuario_id = interes.credito.usuario_id  # may be accessible via relationship if loaded
    except Exception:
        # fallback: load credito
        from models.credito import Credito
        credito = session.get(Credito, interes.credito_id)
        if credito:
            usuario_id = credito.usuario_id

    h = Historial(accion="CREAR", detalle=f"Simulación {sim.id} creada para interés {interes_id}", usuario_id=usuario_id)
    session.add(h)
    session.commit()
    return {"mensaje": "Simulación creada", "simulacion": sim}

@router.get("/listar", response_model=List[Simulacion])
def listar_simulaciones(session: Session = Depends(get_session)):
    return session.exec(select(Simulacion)).all()

@router.get("/{simulacion_id}")
def obtener_simulacion(simulacion_id: int, session: Session = Depends(get_session)):
    sim = session.get(Simulacion, simulacion_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return sim

@router.delete("/{simulacion_id}")
def eliminar_simulacion(simulacion_id: int, session: Session = Depends(get_session)):
    sim = session.get(Simulacion, simulacion_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    # try map to user
    usuario_id = None
    try:
        usuario_id = sim.interes.credito.usuario_id
    except Exception:
        pass

    h = Historial(accion="ELIMINAR", detalle=f"Simulación {sim.id} eliminada", usuario_id=usuario_id)
    session.add(h)
    session.delete(sim)
    session.commit()
    return {"mensaje": "Simulación eliminada y registrada"}
