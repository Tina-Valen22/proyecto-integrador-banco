# routers/historial_router.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.historial import Historial

router = APIRouter(prefix="/historial", tags=["Historial"])


# -----------------------------
# READ - LISTAR / FILTRAR
# -----------------------------
@router.get("/", response_model=List[Historial])
def listar_historial(
    session: Session = Depends(get_session),
    entidad: Optional[str] = Query(
        None, description="Filtrar por entidad (ej: Usuario, Crédito, Interés, etc.)"
    ),
    accion: Optional[str] = Query(
        None, description="Filtrar por acción (CREAR, ACTUALIZAR, ELIMINAR, etc.)"
    ),
    descripcion_contiene: Optional[str] = Query(
        None, description="Texto contenido en la descripción"
    ),
    fecha_desde: Optional[datetime] = Query(
        None, description="Filtrar desde esta fecha (incluida)"
    ),
    fecha_hasta: Optional[datetime] = Query(
        None, description="Filtrar hasta esta fecha (incluida)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
) -> List[Historial]:
    """
    Lista los registros de historial con filtros opcionales:
    - entidad: Usuario, Crédito, Interés, etc.
    - acción: CREAR, ACTUALIZAR, ELIMINAR, etc.
    - texto contenido en la descripción
    - rango de fechas
    - paginación con limit / offset
    """
    query = select(Historial)

    if entidad:
        query = query.where(Historial.entidad == entidad)

    if accion:
        query = query.where(Historial.accion == accion)

    if descripcion_contiene:
        query = query.where(Historial.descripcion.contains(descripcion_contiene))

    if fecha_desde is not None:
        query = query.where(Historial.fecha >= fecha_desde)

    if fecha_hasta is not None:
        query = query.where(Historial.fecha <= fecha_hasta)

    query = query.order_by(Historial.fecha.desc())
    query = query.offset(offset).limit(limit)

    historial = session.exec(query).all()
    return historial


# -----------------------------
# READ - OBTENER POR ID
# -----------------------------
@router.get("/{historial_id}", response_model=Historial)
def obtener_historial(
    historial_id: int,
    session: Session = Depends(get_session),
) -> Historial:
    """
    Obtiene un registro de historial por su id.
    """
    registro = session.get(Historial, historial_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de historial no encontrado")
    return registro


# -----------------------------
# DELETE - OPCIONAL
# -----------------------------
@router.delete("/{historial_id}")
def eliminar_historial(
    historial_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina un registro de historial puntual.
    (En muchos sistemas reales esto no se expone, pero aquí lo dejamos
    disponible por si necesitas limpiar datos de prueba).
    """
    registro = session.get(Historial, historial_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de historial no encontrado")

    session.delete(registro)
    session.commit()

    return {"mensaje": f"Registro de historial {historial_id} eliminado"}