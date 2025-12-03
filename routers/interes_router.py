# routers/interes_router.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models.interes import Interes
from models.credito import Credito
from models.historial import Historial

router = APIRouter(prefix="/intereses", tags=["Intereses"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
def ver_intereses(request: Request, session: Session = Depends(get_session)):
    intereses = session.exec(select(Interes)).all()
    creditos = session.exec(select(Credito)).all()
    return templates.TemplateResponse("intereses.html",
        {"request": request, "intereses": intereses, "creditos": creditos}
    )


@router.post("/crear")
def crear_interes(
    tasa: float = Form(...),
    tipo: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session)
):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    interes = Interes(tasa=tasa, tipo=tipo, credito_id=credito_id)
    session.add(interes)
    session.commit()

    h = Historial(
        accion="CREAR",
        detalle=f"Interés creado para crédito {credito_id}",
        usuario_id=credito.usuario_id
    )

    session.add(h)
    session.commit()

    return RedirectResponse(url="/intereses", status_code=303)


@router.post("/actualizar/{interes_id}")
def actualizar_interes(
    interes_id: int,
    tasa: float = Form(...),
    tipo: str = Form(...),
    session: Session = Depends(get_session)
):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    interes.tasa = tasa
    interes.tipo = tipo
    session.commit()

    h = Historial(
        accion="ACTUALIZAR",
        detalle=f"Interés {interes_id} actualizado",
        usuario_id=interes.credito_id
    )

    session.add(h)
    session.commit()

    return RedirectResponse(url="/intereses", status_code=303)


@router.post("/eliminar/{interes_id}")
def eliminar_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)

    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    h = Historial(
        accion="ELIMINAR",
        detalle=f"Interés {interes_id} eliminado",
        usuario_id=None
    )

    session.add(h)
    session.delete(interes)
    session.commit()

    return RedirectResponse(url="/intereses", status_code=303)
