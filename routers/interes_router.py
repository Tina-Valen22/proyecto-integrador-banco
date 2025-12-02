# routers/interes_router.py
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models.interes import Interes
from models.credito import Credito
from models.historial import Historial
from datetime import datetime
from typing import List

router = APIRouter(prefix="/intereses", tags=["Intereses"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/")
def crear_interes(tasa: float, tipo: str, credito_id: int, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    interes = Interes(tasa=tasa, tipo=tipo, credito_id=credito_id)
    session.add(interes)
    session.commit()
    session.refresh(interes)

    # historial
    h = Historial(entidad="Interés", accion="CREAR",
                  descripcion=f"Interés creado para crédito {credito_id} (tasa={tasa})",
                  fecha=datetime.now())
    session.add(h)
    session.commit()
    return {"mensaje": "Interés creado correctamente", "interes": interes}

@router.get("/", response_model=List[Interes])
def listar_intereses(session: Session = Depends(get_session)):
    return session.exec(select(Interes)).all()

@router.get("/{interes_id}")
def obtener_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")
    return interes

@router.put("/{interes_id}")
def actualizar_interes(interes_id: int, tasa: float, tipo: str, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    interes.tasa = tasa
    interes.tipo = tipo
    session.commit()
    session.refresh(interes)

    h = Historial(entidad="Interés", accion="ACTUALIZAR",
                  descripcion=f"Interés {interes_id} actualizado (tasa={tasa})",
                  fecha=datetime.now())
    session.add(h)
    session.commit()
    return {"mensaje": "Interés actualizado", "interes": interes}

@router.delete("/{interes_id}")
def eliminar_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    h = Historial(entidad="Interés", accion="ELIMINAR",
                  descripcion=f"Interés {interes_id} eliminado",
                  fecha=datetime.now())
    session.add(h)
    session.delete(interes)
    session.commit()
    return {"mensaje": "Interés eliminado y guardado en historial"}
