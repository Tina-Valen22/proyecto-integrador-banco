# routers/historial_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from models.historial import Historial
from models.usuario import Usuario

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/historial", tags=["Historial"])

@router.get("/")
def ver_historial(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(select(Historial)).all()
    # optionally enrich with username
    enriched = []
    for l in logs:
        usuario = session.get(Usuario, l.usuario_id) if getattr(l, "usuario_id", None) else None
        enriched.append({"log": l, "usuario_nombre": usuario.nombre if usuario else None})
    return templates.TemplateResponse("historial.html", {"request": request, "logs": enriched})

@router.get("/listar")
def listar_historial(session: Session = Depends(get_session)):
    return session.exec(select(Historial)).all()

@router.post("/restaurar_usuario")
def restaurar_usuario(nombre: str, ingresos: float, gastos: float, session: Session = Depends(get_session)):
    # create user
    from models.usuario import Usuario
    nuevo = Usuario(nombre=nombre, ingresos=ingresos, gastos=gastos)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    # add historial
    h = Historial(accion="RESTAURAR", detalle=f"Usuario {nombre} restaurado", usuario_id=nuevo.id)
    session.add(h)
    session.commit()
    return {"mensaje": "Usuario restaurado", "usuario": nuevo}
