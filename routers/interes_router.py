from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models.interes import Interes
from models.credito import Credito
from models.historial import Historial
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/intereses", tags=["Intereses"])

# Sesión
def get_session():
    with Session(engine) as session:
        yield session


# ✅ Crear interés (asociado a un crédito existente)
@router.post("/")
def crear_interes(
    tasa: float,
    tipo: str,
    credito_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    # Verificar que el crédito exista
    if credito_id is not None:
        credito = session.get(Credito, credito_id)
        if not credito:
            raise HTTPException(status_code=404, detail="Crédito no encontrado")
    else:
        raise HTTPException(status_code=400, detail="Debe especificar un crédito asociado")

    interes = Interes(tasa=tasa, tipo=tipo, credito_id=credito_id)
    session.add(interes)
    session.commit()
    session.refresh(interes)

    # Registrar en historial
    historial = Historial(
        entidad="Interés",
        accion="CREAR",
        descripcion=f"Se creó un interés tipo '{tipo}' con tasa {tasa}% para el crédito {credito_id}",
        fecha=datetime.now()
    )
    session.add(historial)
    session.commit()

    return {"mensaje": "Interés creado exitosamente", "interes": interes}


# ✅ Listar todos los intereses
@router.get("/", response_model=List[Interes])
def listar_intereses(session: Session = Depends(get_session)):
    intereses = session.exec(select(Interes)).all()
    if not intereses:
        raise HTTPException(status_code=404, detail="No hay intereses registrados")
    return intereses


# ✅ Obtener interés por ID
@router.get("/{interes_id}")
def obtener_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")
    return interes


# ✅ Actualizar interés
@router.put("/{interes_id}")
def actualizar_interes(interes_id: int, datos: Interes, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    interes.tasa = datos.tasa
    interes.tipo = datos.tipo
    session.commit()
    session.refresh(interes)

    # Registrar actualización
    historial = Historial(
        entidad="Interés",
        accion="ACTUALIZAR",
        descripcion=f"Interés {interes_id} actualizado (tasa: {datos.tasa}, tipo: {datos.tipo})",
        fecha=datetime.now()
    )
    session.add(historial)
    session.commit()

    return {"mensaje": "Interés actualizado exitosamente", "interes": interes}


# ✅ Eliminar interés
@router.delete("/{interes_id}")
def eliminar_interes(interes_id: int, session: Session = Depends(get_session)):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    historial = Historial(
        entidad="Interés",
        accion="ELIMINAR",
        descripcion=f"Interés {interes_id} eliminado",
        fecha=datetime.now()
    )
    session.add(historial)
    session.delete(interes)
    session.commit()
    return {"mensaje": "Interés eliminado correctamente"}
 