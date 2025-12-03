# routers/historial_router.py
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from models.historial import Historial
from models.usuario import Usuario

router = APIRouter(prefix="/historial", tags=["Historial"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
def ver_historial(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(select(Historial)).all()
    enriched = []

    for l in logs:
        usuario = session.get(Usuario, l.usuario_id) if l.usuario_id else None
        enriched.append({
            "log": l,
            "usuario_nombre": usuario.nombre if usuario else "N/A"
        })

    return templates.TemplateResponse(
        "historial.html",
        {"request": request, "logs": enriched}
    )
