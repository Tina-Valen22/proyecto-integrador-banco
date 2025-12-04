from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.credito import Credito
from models.usuario import Usuario
from models.historial import Historial

router = APIRouter(prefix="/creditos", tags=["Créditos"])


# -----------------------------
# CREATE
# -----------------------------
@router.post("/", response_model=Credito)
def crear_credito(
    credito: Credito,
    session: Session = Depends(get_session)
) -> Credito:
    """
    Crea un crédito asociado a un usuario existente
    y registra la acción en el historial.
    """
    # Validar que el usuario exista
    usuario = session.get(Usuario, credito.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=400,
            detail=f"El usuario con id {credito.usuario_id} no existe",
        )

    session.add(credito)
    session.commit()
    session.refresh(credito)

    historial = Historial(
        entidad="Crédito",
        accion="CREAR",
        descripcion=(
            f"Crédito creado con id {credito.idCredito}, "
            f"monto {credito.monto}, plazo {credito.plazo} meses, "
            f"tipo '{credito.tipo}', para el usuario '{usuario.nombre}' (id {usuario.idUsuario})"
        ),
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return credito


# -----------------------------
# READ - LISTAR / FILTRAR
# -----------------------------
@router.get("/", response_model=List[Credito])
def listar_creditos(
    session: Session = Depends(get_session),
    usuario_id: Optional[int] = Query(
        None, description="Filtrar por id de usuario"
    ),
    tipo: Optional[str] = Query(
        None, description="Filtrar por tipo de crédito"
    ),
    monto_min: Optional[float] = Query(
        None, description="Monto mínimo"
    ),
    monto_max: Optional[float] = Query(
        None, description="Monto máximo"
    ),
) -> List[Credito]:
    """
    Lista todos los créditos, con filtros opcionales:
    - usuario_id
    - tipo
    - monto mínimo / máximo
    """
    query = select(Credito)

    if usuario_id is not None:
        query = query.where(Credito.usuario_id == usuario_id)

    if tipo:
        query = query.where(Credito.tipo == tipo)

    if monto_min is not None:
        query = query.where(Credito.monto >= monto_min)

    if monto_max is not None:
        query = query.where(Credito.monto <= monto_max)

    creditos = session.exec(query).all()
    return creditos


# -----------------------------
# READ - OBTENER POR ID
# -----------------------------
@router.get("/{credito_id}", response_model=Credito)
def obtener_credito(
    credito_id: int,
    session: Session = Depends(get_session)
) -> Credito:
    """
    Obtiene un crédito por su id.
    """
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    return credito


# -----------------------------
# UPDATE COMPLETO (PUT)
# -----------------------------
@router.put("/{credito_id}", response_model=Credito)
def actualizar_credito(
    credito_id: int,
    datos: Credito,
    session: Session = Depends(get_session),
) -> Credito:
    """
    Reemplaza completamente los datos de un crédito existente.
    """
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    # Validar que el nuevo usuario exista
    usuario = session.get(Usuario, datos.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=400,
            detail=f"El usuario con id {datos.usuario_id} no existe",
        )

    credito.monto = datos.monto
    credito.plazo = datos.plazo
    credito.tipo = datos.tipo
    credito.descripcion = datos.descripcion
    credito.usuario_id = datos.usuario_id

    session.commit()
    session.refresh(credito)

    historial = Historial(
        entidad="Crédito",
        accion="ACTUALIZAR",
        descripcion=(
            f"Crédito id {credito.idCredito} actualizado. "
            f"Monto {credito.monto}, plazo {credito.plazo}, tipo '{credito.tipo}', "
            f"usuario id {credito.usuario_id}"
        ),
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return credito


# -----------------------------
# UPDATE PARCIAL (PATCH)
# -----------------------------
@router.patch("/{credito_id}", response_model=Credito)
def actualizar_credito_parcial(
    credito_id: int,
    monto: Optional[float] = None,
    plazo: Optional[int] = None,
    tipo: Optional[str] = None,
    descripcion: Optional[str] = None,
    usuario_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> Credito:
    """
    Actualiza parcialmente un crédito. Solo se modifican los campos enviados.
    """
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    cambios = []

    if monto is not None:
        credito.monto = monto
        cambios.append("monto")
    if plazo is not None:
        credito.plazo = plazo
        cambios.append("plazo")
    if tipo is not None:
        credito.tipo = tipo
        cambios.append("tipo")
    if descripcion is not None:
        credito.descripcion = descripcion
        cambios.append("descripcion")
    if usuario_id is not None:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario con id {usuario_id} no existe",
            )
        credito.usuario_id = usuario_id
        cambios.append("usuario_id")

    if cambios:
        session.commit()
        session.refresh(credito)

        detalle_cambios = ", ".join(cambios)
        historial = Historial(
            entidad="Crédito",
            accion="ACTUALIZAR_PARCIAL",
            descripcion=(
                f"Crédito id {credito.idCredito} actualizado parcialmente. "
                f"Campos modificados: {detalle_cambios}"
            ),
            fecha=datetime.now(),
        )
        session.add(historial)
        session.commit()

    return credito


# -----------------------------
# DELETE
# -----------------------------
@router.delete("/{credito_id}")
def eliminar_credito(
    credito_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina un crédito y registra la acción en el historial.
    """
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    historial = Historial(
        entidad="Crédito",
        accion="ELIMINAR",
        descripcion=f"Crédito id {credito.idCredito} eliminado",
        fecha=datetime.now(),
    )
    session.add(historial)

    session.delete(credito)
    session.commit()

    return {"mensaje": "Crédito eliminado correctamente y registrado en historial"}