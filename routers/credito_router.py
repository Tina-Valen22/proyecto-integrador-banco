# routers/credito_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models.credito import Credito
from models.usuario import Usuario
from models.historial import Historial

router = APIRouter(prefix="/creditos", tags=["Créditos"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
def ver_creditos(request: Request, session: Session = Depends(get_session)):
    creditos = session.exec(select(Credito)).all()
    usuarios = session.exec(select(Usuario)).all()
    return templates.TemplateResponse("creditos.html",
        {"request": request, "creditos": creditos, "usuarios": usuarios}
    )


@router.post("/crear")
def crear_credito(
    monto: float = Form(...),
    plazo: int = Form(...),
    tipo: str = Form(...),
    usuario_id: int = Form(...),
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    credito = Credito(monto=monto, plazo=plazo, tipo=tipo, usuario_id=usuario_id)
    session.add(credito)
    session.commit()
    session.refresh(credito)

    historial = Historial(
        accion="CREAR",
        detalle=f"Crédito creado para usuario {usuario.nombre}",
        usuario_id=usuario.id
    )

    session.add(historial)
    session.commit()

    return RedirectResponse(url="/creditos", status_code=303)


@router.post("/actualizar/{credito_id}")
def actualizar_credito(
    credito_id: int,
    monto: float = Form(...),
    plazo: int = Form(...),
    tipo: str = Form(...),
    session: Session = Depends(get_session)
):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    credito.monto = monto
    credito.plazo = plazo
    credito.tipo = tipo

    session.commit()
    session.refresh(credito)

    historial = Historial(
        accion="ACTUALIZAR",
        detalle=f"Crédito {credito_id} actualizado",
        usuario_id=credito.usuario_id
    )
    session.add(historial)
    session.commit()

    return RedirectResponse(url="/creditos", status_code=303)


@router.post("/eliminar/{credito_id}")
def eliminar_credito(credito_id: int, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    historial = Historial(
        accion="ELIMINAR",
        detalle=f"Crédito {credito_id} eliminado",
        usuario_id=credito.usuario_id
    )
    session.add(historial)

    session.delete(credito)
    session.commit()

    return RedirectResponse(url="/creditos", status_code=303)
