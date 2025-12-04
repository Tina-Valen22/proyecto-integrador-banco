# routers/interes_router.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query, Form, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from database import get_session
from models.interes import Interes
from models.credito import Credito
from models.historial import Historial

router = APIRouter(prefix="/intereses", tags=["Intereses"])


# -----------------------------
# CREATE (API JSON)
# -----------------------------
@router.post("/", response_model=Interes)
def crear_interes(
    tasa: float,
    tipo: str,
    credito_id: int,
    session: Session = Depends(get_session),
) -> Interes:
    """
    Crea un interés asociado a un crédito existente
    y registra la acción en el historial.
    """
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    interes = Interes(tasa=tasa, tipo=tipo, credito_id=credito_id)
    session.add(interes)
    session.commit()
    session.refresh(interes)

    h = Historial(
        entidad="Interés",
        accion="CREAR",
        descripcion=(
            f"Interés creado para crédito {credito_id} "
            f"(tasa={tasa}, tipo='{tipo}')"
        ),
        fecha=datetime.now(),
    )
    session.add(h)
    session.commit()

    return interes


# -----------------------------
# READ - LISTAR / FILTRAR (API JSON)
# -----------------------------
@router.get("/", response_model=List[Interes])
def listar_intereses(
    session: Session = Depends(get_session),
    credito_id: Optional[int] = Query(
        None, description="Filtrar por id de crédito"
    ),
    tipo: Optional[str] = Query(
        None, description="Filtrar por tipo de interés"
    ),
    tasa_min: Optional[float] = Query(
        None, description="Filtrar por tasa mínima"
    ),
    tasa_max: Optional[float] = Query(
        None, description="Filtrar por tasa máxima"
    ),
) -> List[Interes]:
    """
    Lista todos los intereses, con filtros opcionales:
    - crédito
    - tipo
    - rango de tasas
    """
    query = select(Interes)

    if credito_id is not None:
        query = query.where(Interes.credito_id == credito_id)

    if tipo:
        query = query.where(Interes.tipo == tipo)

    if tasa_min is not None:
        query = query.where(Interes.tasa >= tasa_min)

    if tasa_max is not None:
        query = query.where(Interes.tasa <= tasa_max)

    intereses = session.exec(query).all()
    return intereses


# -----------------------------
# READ - OBTENER POR ID (API JSON)
# -----------------------------
@router.get("/{interes_id}", response_model=Interes)
def obtener_interes(
    interes_id: int,
    session: Session = Depends(get_session),
) -> Interes:
    """
    Obtiene un interés por su id.
    """
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")
    return interes


# -----------------------------
# UPDATE COMPLETO (PUT, API JSON)
# -----------------------------
@router.put("/{interes_id}", response_model=Interes)
def actualizar_interes(
    interes_id: int,
    tasa: float,
    tipo: str,
    credito_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> Interes:
    """
    Reemplaza completamente los datos de un interés existente.
    Permite opcionalmente cambiar el crédito asociado.
    """
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    if credito_id is not None:
        credito = session.get(Credito, credito_id)
        if not credito:
            raise HTTPException(
                status_code=404,
                detail=f"Crédito con id {credito_id} no encontrado",
            )
        interes.credito_id = credito_id

    interes.tasa = tasa
    interes.tipo = tipo

    session.commit()
    session.refresh(interes)

    h = Historial(
        entidad="Interés",
        accion="ACTUALIZAR",
        descripcion=(
            f"Interés {interes_id} actualizado "
            f"(tasa={tasa}, tipo='{tipo}', credito_id={interes.credito_id})"
        ),
        fecha=datetime.now(),
    )
    session.add(h)
    session.commit()

    return interes


# -----------------------------
# UPDATE PARCIAL (PATCH, API JSON)
# -----------------------------
@router.patch("/{interes_id}", response_model=Interes)
def actualizar_interes_parcial(
    interes_id: int,
    tasa: Optional[float] = None,
    tipo: Optional[str] = None,
    credito_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> Interes:
    """
    Actualiza parcialmente un interés. Solo se modifican los campos enviados.
    """
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    cambios = []

    if tasa is not None:
        interes.tasa = tasa
        cambios.append("tasa")

    if tipo is not None:
        interes.tipo = tipo
        cambios.append("tipo")

    if credito_id is not None:
        credito = session.get(Credito, credito_id)
        if not credito:
            raise HTTPException(
                status_code=404,
                detail=f"Crédito con id {credito_id} no encontrado",
            )
        interes.credito_id = credito_id
        cambios.append("credito_id")

    if cambios:
        session.commit()
        session.refresh(interes)

        detalle_cambios = ", ".join(cambios)
        h = Historial(
            entidad="Interés",
            accion="ACTUALIZAR_PARCIAL",
            descripcion=(
                f"Interés {interes_id} actualizado parcialmente. "
                f"Campos modificados: {detalle_cambios}"
            ),
            fecha=datetime.now(),
        )
        session.add(h)
        session.commit()

    return interes


# -----------------------------
# DELETE (API JSON)
# -----------------------------
@router.delete("/{interes_id}")
def eliminar_interes(
    interes_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina un interés y registra la acción en el historial.
    """
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    h = Historial(
        entidad="Interés",
        accion="ELIMINAR",
        descripcion=f"Interés {interes_id} eliminado",
        fecha=datetime.now(),
    )
    session.add(h)
    session.delete(interes)
    session.commit()

    return {"mensaje": "Interés eliminado y guardado en historial"}


# -----------------------------------------
# Endpoints para formularios HTML (UI)
# -----------------------------------------

@router.post("/crear")
def crear_interes_form(
    tasa: str = Form(...),
    tipo: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    """
    Crea un interés desde el formulario HTML y redirige a /ui/intereses.
    Campos obligatorios:
    - crédito
    - tasa (0 < tasa <= 100)
    - tipo
    """
    # Validar crédito
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=400, detail="Crédito no encontrado")

    # Normalizar y validar tasa
    tasa_str = tasa.strip().replace("%", "").replace(",", ".")
    try:
        tasa_val = float(tasa_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="La tasa debe ser un número válido",
        )

    if tasa_val <= 0 or tasa_val > 100:
        raise HTTPException(
            status_code=400,
            detail="La tasa debe ser mayor que 0 y menor o igual a 100",
        )

    if not tipo.strip():
        raise HTTPException(
            status_code=400,
            detail="El tipo de interés es obligatorio",
        )

    interes = Interes(
        tasa=tasa_val,
        tipo=tipo.strip(),
        credito_id=credito_id,
    )
    session.add(interes)
    session.commit()
    session.refresh(interes)

    h = Historial(
        entidad="Interés",
        accion="CREAR",
        descripcion=(
            f"Interés creado para crédito {credito_id} "
            f"(tasa={tasa_val}, tipo='{tipo.strip()}')"
        ),
        fecha=datetime.now(),
    )
    session.add(h)
    session.commit()

    return RedirectResponse(url="/ui/intereses", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/actualizar")
def actualizar_interes_form(
    idInteres: int = Form(...),
    tasa: str = Form(...),
    tipo: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    """
    Actualiza un interés desde el formulario HTML y redirige a /ui/intereses.
    Todos los campos son obligatorios.
    """
    interes = session.get(Interes, idInteres)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    # Validar crédito
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=400, detail="Crédito no encontrado")

    # Normalizar y validar tasa
    tasa_str = tasa.strip().replace("%", "").replace(",", ".")
    try:
        tasa_val = float(tasa_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="La tasa debe ser un número válido",
        )

    if tasa_val <= 0 or tasa_val > 100:
        raise HTTPException(
            status_code=400,
            detail="La tasa debe ser mayor que 0 y menor o igual a 100",
        )

    if not tipo.strip():
        raise HTTPException(
            status_code=400,
            detail="El tipo de interés es obligatorio",
        )

    interes.tasa = tasa_val
    interes.tipo = tipo.strip()
    interes.credito_id = credito_id

    session.add(interes)
    session.commit()
    session.refresh(interes)

    h = Historial(
        entidad="Interés",
        accion="ACTUALIZAR",
        descripcion=(
            f"Interés {idInteres} actualizado "
            f"(tasa={tasa_val}, tipo='{interes.tipo}', credito_id={interes.credito_id})"
        ),
        fecha=datetime.now(),
    )
    session.add(h)
    session.commit()

    return RedirectResponse(url="/ui/intereses", status_code=status.HTTP_303_SEE_OTHER)