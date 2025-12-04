# routers/simulacion_router.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select

from database import get_session
from models.simulacion import Simulacion
from models.interes import Interes
from models.historial import Historial

router = APIRouter(prefix="/simulaciones", tags=["Simulaciones"])


# -----------------------------
# CREATE
# -----------------------------
@router.post("/", response_model=Simulacion)
def crear_simulacion(
    simulacion: Simulacion,
    session: Session = Depends(get_session),
) -> Simulacion:
    """
    Crea una simulación asociada a un interés existente
    y registra la acción en el historial.
    """
    interes = session.get(Interes, simulacion.interes_id)
    if not interes:
        raise HTTPException(
            status_code=400,
            detail=f"El interés con id {simulacion.interes_id} no existe",
        )

    session.add(simulacion)
    session.commit()
    session.refresh(simulacion)

    historial = Historial(
        entidad="Simulación",
        accion="CREAR",
        descripcion=(
            f"Simulación {simulacion.idSimulacion} creada "
            f"(cuotaMensual={simulacion.cuotaMensual}, "
            f"interesTotal={simulacion.interesTotal}, "
            f"saldoFinal={simulacion.saldoFinal}, "
            f"interes_id={simulacion.interes_id})"
        ),
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return simulacion


# -----------------------------
# READ - LISTAR / FILTRAR
# -----------------------------
@router.get("/", response_model=List[Simulacion])
def listar_simulaciones(
    session: Session = Depends(get_session),
    interes_id: Optional[int] = Query(
        None, description="Filtrar por id de interés"
    ),
    cuota_min: Optional[float] = Query(
        None, description="Filtrar por cuota mensual mínima"
    ),
    cuota_max: Optional[float] = Query(
        None, description="Filtrar por cuota mensual máxima"
    ),
) -> List[Simulacion]:
    """
    Lista todas las simulaciones, con filtros opcionales por:
    - interés
    - rango de cuota mensual
    """
    query = select(Simulacion)

    if interes_id is not None:
        query = query.where(Simulacion.interes_id == interes_id)

    if cuota_min is not None:
        query = query.where(Simulacion.cuotaMensual >= cuota_min)

    if cuota_max is not None:
        query = query.where(Simulacion.cuotaMensual <= cuota_max)

    simulaciones = session.exec(query).all()
    return simulaciones


# -----------------------------
# READ - OBTENER POR ID
# -----------------------------
@router.get("/{simulacion_id}", response_model=Simulacion)
def obtener_simulacion(
    simulacion_id: int,
    session: Session = Depends(get_session),
) -> Simulacion:
    """
    Obtiene una simulación por su id.
    """
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return simulacion


# -----------------------------
# UPDATE COMPLETO (PUT)
# -----------------------------
@router.put("/{simulacion_id}", response_model=Simulacion)
def actualizar_simulacion(
    simulacion_id: int,
    datos: Simulacion,
    session: Session = Depends(get_session),
) -> Simulacion:
    """
    Reemplaza completamente los datos de una simulación.
    """
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    # Validar interés si cambia
    if datos.interes_id != simulacion.interes_id:
        interes = session.get(Interes, datos.interes_id)
        if not interes:
            raise HTTPException(
                status_code=400,
                detail=f"El interés con id {datos.interes_id} no existe",
            )
        simulacion.interes_id = datos.interes_id

    simulacion.cuotaMensual = datos.cuotaMensual
    simulacion.interesTotal = datos.interesTotal
    simulacion.saldoFinal = datos.saldoFinal

    session.commit()
    session.refresh(simulacion)

    historial = Historial(
        entidad="Simulación",
        accion="ACTUALIZAR",
        descripcion=(
            f"Simulación {simulacion.idSimulacion} actualizada "
            f"(cuotaMensual={simulacion.cuotaMensual}, "
            f"interesTotal={simulacion.interesTotal}, "
            f"saldoFinal={simulacion.saldoFinal}, "
            f"interes_id={simulacion.interes_id})"
        ),
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return simulacion


# -----------------------------
# UPDATE PARCIAL (PATCH)
# -----------------------------
@router.patch("/{simulacion_id}", response_model=Simulacion)
def actualizar_simulacion_parcial(
    simulacion_id: int,
    cuotaMensual: Optional[float] = None,
    interesTotal: Optional[float] = None,
    saldoFinal: Optional[float] = None,
    interes_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> Simulacion:
    """
    Actualiza parcialmente una simulación.
    Solo se modifican los campos enviados.
    """
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    cambios = []

    if cuotaMensual is not None:
        simulacion.cuotaMensual = cuotaMensual
        cambios.append("cuotaMensual")

    if interesTotal is not None:
        simulacion.interesTotal = interesTotal
        cambios.append("interesTotal")

    if saldoFinal is not None:
        simulacion.saldoFinal = saldoFinal
        cambios.append("saldoFinal")

    if interes_id is not None:
        interes = session.get(Interes, interes_id)
        if not interes:
            raise HTTPException(
                status_code=400,
                detail=f"El interés con id {interes_id} no existe",
            )
        simulacion.interes_id = interes_id
        cambios.append("interes_id")

    if cambios:
        session.commit()
        session.refresh(simulacion)

        detalle_cambios = ", ".join(cambios)
        historial = Historial(
            entidad="Simulación",
            accion="ACTUALIZAR_PARCIAL",
            descripcion=(
                f"Simulación {simulacion.idSimulacion} actualizada parcialmente. "
                f"Campos modificados: {detalle_cambios}"
            ),
            fecha=datetime.now(),
        )
        session.add(historial)
        session.commit()

    return simulacion


# -----------------------------
# DELETE
# -----------------------------
@router.delete("/{simulacion_id}")
def eliminar_simulacion(
    simulacion_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina una simulación y registra la acción en el historial.
    """
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    historial = Historial(
        entidad="Simulación",
        accion="ELIMINAR",
        descripcion=f"Simulación {simulacion.idSimulacion} eliminada",
        fecha=datetime.now(),
    )
    session.add(historial)
    session.delete(simulacion)
    session.commit()

    return {"mensaje": "Simulación eliminada y registrada en historial"}