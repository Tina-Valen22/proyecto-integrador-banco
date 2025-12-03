# routers/interes_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from models.interes import Interes
from models.credito import Credito
from models.historial import Historial
from typing import List
from datetime import datetime

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/intereses", tags=["Intereses"])

@router.get("/")
def ver_intereses(request: Request, session: Session = Depends(get_session)):
    intereses = session.exec(select(Interes)).all()
    return templates.TemplateResponse("intereses.html", {"request": request, "intereses": intereses})

@router.post("/crear")
def crear_interes(tasa: float = Form(...), tipo: str = Form(...), credito_id: int = Form(...), session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    interes = Interes(tasa=tasa, tipo=tipo, credito_id=credito_id)
    session.add(interes)
    session.commit()
    session.refresh(interes)

    h = Historial(accion="CREAR", detalle=f"Interés (tasa={tasa}, tipo={tipo}) creado para crédito {credito_id}", usuario_id=credito.usuario_id)
    session.add(h)
    session.commit()
    return {"mensaje": "Interés creado", "interes": interes}

@router.get("/listar", response_model=List[Interes])
def listar_intereses(session: Session = Depends(get_session)):
    return session.exec(select(Interes)).all()

@router.get("/{interes_id}")
def obtener_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")
    return interes

@router.put("/{interes_id}")
def actualizar_interes(interes_id: int, tasa: float = Form(...), tipo: str = Form(...), session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    interes.tasa = tasa
    interes.tipo = tipo
    session.commit()
    session.refresh(interes)

    h = Historial(accion="ACTUALIZAR", detalle=f"Interés {interes_id} actualizado", usuario_id=interes.credito_id)
    session.add(h)
    session.commit()
    return {"mensaje": "Interés actualizado", "interes": interes}

@router.delete("/{interes_id}")
def eliminar_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    # find usuario id via credito if possible
    usuario_id = None
    credito = session.get(Credito, interes.credito_id) if interes.credito_id else None
    if credito:
        usuario_id = credito.usuario_id

    h = Historial(accion="ELIMINAR", detalle=f"Interés {interes_id} eliminado", usuario_id=usuario_id)
    session.add(h)

    session.delete(interes)
    session.commit()
    return {"mensaje": "Interés eliminado y registrado"}
