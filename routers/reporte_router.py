# routers/reporte_router.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.reporte import Reporte
from models.usuario import Usuario
from models.credito import Credito
from models.simulacion import Simulacion
from models.historial import Historial

router = APIRouter(prefix="/reportes", tags=["Reportes"])


# -----------------------------
# HELPERS
# -----------------------------
def _validar_relaciones_reporte(
    session: Session,
    usuario_id: Optional[int],
    credito_id: Optional[int],
    simulacion_id: Optional[int],
) -> None:
    """
    Valida que los IDs relacionados (usuario, crédito, simulación)
    existan en la base de datos si no son None.
    """
    if usuario_id is not None:
        usuario = session.get(Usuario, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario con id {usuario_id} no existe",
            )

    if credito_id is not None:
        credito = session.get(Credito, credito_id)
        if not credito:
            raise HTTPException(
                status_code=400,
                detail=f"El crédito con id {credito_id} no existe",
            )

    if simulacion_id is not None:
        simulacion = session.get(Simulacion, simulacion_id)
        if not simulacion:
            raise HTTPException(
                status_code=400,
                detail=f"La simulación con id {simulacion_id} no existe",
            )


# -----------------------------
# CREATE
# -----------------------------
@router.post("/", response_model=Reporte)
def crear_reporte(
    reporte: Reporte,
    session: Session = Depends(get_session),
) -> Reporte:
    """
    Crea un reporte y registra la acción en el historial.
    Valida que las entidades relacionadas existan si se envían.
    """

    _validar_relaciones_reporte(
        session,
        usuario_id=reporte.usuario_id,
        credito_id=reporte.credito_id,
        simulacion_id=reporte.simulacion_id,
    )

    # Si no viene fecha, la ponemos a ahora
    if not reporte.fecha:
        reporte.fecha = datetime.now()

    session.add(reporte)
    session.commit()
    session.refresh(reporte)

    historial = Historial(
        entidad="Reporte",
        accion="CREAR",
        descripcion=(
            f"Reporte '{reporte.titulo}' creado con id {reporte.idReporte}. "
            f"Usuario_id={reporte.usuario_id}, Credito_id={reporte.credito_id}, "
            f"Simulacion_id={reporte.simulacion_id}"
        ),
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return reporte


# -----------------------------
# READ - LISTAR / FILTRAR
# -----------------------------
@router.get("/", response_model=List[Reporte])
def listar_reportes(
    session: Session = Depends(get_session),
    usuario_id: Optional[int] = Query(
        None, description="Filtrar por id de usuario asociado"
    ),
    credito_id: Optional[int] = Query(
        None, description="Filtrar por id de crédito asociado"
    ),
    simulacion_id: Optional[int] = Query(
        None, description="Filtrar por id de simulación asociada"
    ),
    fecha_desde: Optional[datetime] = Query(
        None, description="Filtrar desde fecha (incluida)"
    ),
    fecha_hasta: Optional[datetime] = Query(
        None, description="Filtrar hasta fecha (incluida)"
    ),
    titulo_contiene: Optional[str] = Query(
        None, description="Filtrar por texto contenido en el título"
    ),
) -> List[Reporte]:
    """
    Lista reportes con múltiples filtros opcionales:
    - usuario_id, credito_id, simulacion_id
    - rango de fechas
    - texto contenido en el título
    """
    query = select(Reporte)

    if usuario_id is not None:
        query = query.where(Reporte.usuario_id == usuario_id)

    if credito_id is not None:
        query = query.where(Reporte.credito_id == credito_id)

    if simulacion_id is not None:
        query = query.where(Reporte.simulacion_id == simulacion_id)

    if fecha_desde is not None:
        query = query.where(Reporte.fecha >= fecha_desde)

    if fecha_hasta is not None:
        query = query.where(Reporte.fecha <= fecha_hasta)

    if titulo_contiene:
        query = query.where(Reporte.titulo.contains(titulo_contiene))

    reportes = session.exec(query).all()
    return reportes


# -----------------------------
# READ - OBTENER POR ID
# -----------------------------
@router.get("/{reporte_id}", response_model=Reporte)
def obtener_reporte(
    reporte_id: int,
    session: Session = Depends(get_session),
) -> Reporte:
    """
    Obtiene un reporte por su id.
    """
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return reporte


# -----------------------------
# UPDATE COMPLETO (PUT)
# -----------------------------
@router.put("/{reporte_id}", response_model=Reporte)
def actualizar_reporte(
    reporte_id: int,
    datos: Reporte,
    session: Session = Depends(get_session),
) -> Reporte:
    """
    Reemplaza completamente los datos de un reporte.
    """
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    _validar_relaciones_reporte(
        session,
        usuario_id=datos.usuario_id,
        credito_id=datos.credito_id,
        simulacion_id=datos.simulacion_id,
    )

    reporte.titulo = datos.titulo
    reporte.descripcion = datos.descripcion
    reporte.fecha = datos.fecha or reporte.fecha
    reporte.usuario_id = datos.usuario_id
    reporte.credito_id = datos.credito_id
    reporte.simulacion_id = datos.simulacion_id

    session.commit()
    session.refresh(reporte)

    historial = Historial(
        entidad="Reporte",
        accion="ACTUALIZAR",
        descripcion=(
            f"Reporte id {reporte.idReporte} actualizado. "
            f"Titulo='{reporte.titulo}', fecha={reporte.fecha}, "
            f"Usuario_id={reporte.usuario_id}, "
            f"Credito_id={reporte.credito_id}, "
            f"Simulacion_id={reporte.simulacion_id}"
        ),
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return reporte


# -----------------------------
# UPDATE PARCIAL (PATCH)
# -----------------------------
@router.patch("/{reporte_id}", response_model=Reporte)
def actualizar_reporte_parcial(
    reporte_id: int,
    titulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    fecha: Optional[datetime] = None,
    usuario_id: Optional[int] = None,
    credito_id: Optional[int] = None,
    simulacion_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> Reporte:
    """
    Actualiza parcialmente un reporte. Solo los campos enviados son modificados.
    """
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Validar relaciones solo si vienen nuevas
    _validar_relaciones_reporte(
        session,
        usuario_id=usuario_id if usuario_id is not None else reporte.usuario_id,
        credito_id=credito_id if credito_id is not None else reporte.credito_id,
        simulacion_id=(
            simulacion_id if simulacion_id is not None else reporte.simulacion_id
        ),
    )

    cambios = []

    if titulo is not None:
        reporte.titulo = titulo
        cambios.append("titulo")

    if descripcion is not None:
        reporte.descripcion = descripcion
        cambios.append("descripcion")

    if fecha is not None:
        reporte.fecha = fecha
        cambios.append("fecha")

    if usuario_id is not None:
        reporte.usuario_id = usuario_id
        cambios.append("usuario_id")

    if credito_id is not None:
        reporte.credito_id = credito_id
        cambios.append("credito_id")

    if simulacion_id is not None:
        reporte.simulacion_id = simulacion_id
        cambios.append("simulacion_id")

    if cambios:
        session.commit()
        session.refresh(reporte)

        detalle_cambios = ", ".join(cambios)
        historial = Historial(
            entidad="Reporte",
            accion="ACTUALIZAR_PARCIAL",
            descripcion=(
                f"Reporte id {reporte.idReporte} actualizado parcialmente. "
                f"Campos modificados: {detalle_cambios}"
            ),
            fecha=datetime.now(),
        )
        session.add(historial)
        session.commit()

    return reporte


# -----------------------------
# DELETE
# -----------------------------
@router.delete("/{reporte_id}")
def eliminar_reporte(
    reporte_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina un reporte y registra la acción en el historial.
    """
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    historial = Historial(
        entidad="Reporte",
        accion="ELIMINAR",
        descripcion=f"Reporte '{reporte.titulo}' (id {reporte.idReporte}) eliminado",
        fecha=datetime.now(),
    )
    session.add(historial)
    session.delete(reporte)
    session.commit()

    return {"mensaje": "Reporte eliminado y registrado en historial"}