# routers/reporte_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models.reporte import Reporte
from models.simulacion import Simulacion
from models.historial import Historial

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/")
def ver_reportes(request: Request, session: Session = Depends(get_session)):
    reportes = session.exec(select(Reporte)).all()
    sims = session.exec(select(Simulacion)).all()
    return templates.TemplateResponse(
        "reportes.html",
        {"request": request, "reportes": reportes, "simulaciones": sims}
    )


@router.post("/crear")
def crear_reporte(
    grafico: str = Form(...),
    estadisticas: str = Form(...),
    simulacion_id: int = Form(...),
    session: Session = Depends(get_session)
):
    sim = session.get(Simulacion, simulacion_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    rep = Reporte(
        grafico=grafico,
        estadisticas=estadisticas,
        simulacion_id=simulacion_id
    )

    session.add(rep)
    session.commit()

    h = Historial(
        accion="CREAR",
        detalle=f"Reporte creado para simulación {simulacion_id}",
        usuario_id=None
    )

    session.add(h)
    session.commit()

    return RedirectResponse(url="/reportes", status_code=303)


@router.post("/eliminar/{reporte_id}")
def eliminar_reporte(reporte_id: int, session: Session = Depends(get_session)):
    rep = session.get(Reporte, reporte_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    h = Historial(
        accion="ELIMINAR",
        detalle=f"Reporte {reporte_id} eliminado",
        usuario_id=None
    )

    session.add(h)
    session.delete(rep)
    session.commit()

    return RedirectResponse(url="/reportes", status_code=303)
