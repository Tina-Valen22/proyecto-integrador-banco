# routers/simulacion_router.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models.simulacion import Simulacion
from models.interes import Interes
from models.credito import Credito
from models.historial import Historial

router = APIRouter(prefix="/simulaciones", tags=["Simulaciones"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
def ver_simulaciones(request: Request, session: Session = Depends(get_session)):
    sims = session.exec(select(Simulacion)).all()
    intereses = session.exec(select(Interes)).all()
    return templates.TemplateResponse("simulaciones.html",
        {"request": request, "simulaciones": sims, "intereses": intereses}
    )


@router.post("/crear")
def crear_simulacion(
    cuota_mensual: float = Form(...),
    interes_total: float = Form(...),
    saldo_final: float = Form(...),
    interes_id: int = Form(...),
    session: Session = Depends(get_session)
):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    sim = Simulacion(
        cuota_mensual=cuota_mensual,
        interes_total=interes_total,
        saldo_final=saldo_final,
        interes_id=interes_id
    )

    session.add(sim)
    session.commit()

    credito = session.get(Credito, interes.credito_id)
    usuario_id = credito.usuario_id if credito else None

    h = Historial(
        accion="CREAR",
        detalle=f"Simulación creada para interés {interes_id}",
        usuario_id=usuario_id
    )

    session.add(h)
    session.commit()

    return RedirectResponse(url="/simulaciones", status_code=303)


@router.post("/eliminar/{simulacion_id}")
def eliminar_simulacion(simulacion_id: int, session: Session = Depends(get_session)):
    sim = session.get(Simulacion, simulacion_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    h = Historial(
        accion="ELIMINAR",
        detalle=f"Simulación {simulacion_id} eliminada",
        usuario_id=None
    )

    session.add(h)
    session.delete(sim)
    session.commit()

    return RedirectResponse(url="/simulaciones", status_code=303)
