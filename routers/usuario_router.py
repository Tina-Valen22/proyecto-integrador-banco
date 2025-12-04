from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select

from database import get_session
from models.usuario import Usuario
from models.historial import Historial

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# -----------------------------
# CREATE
# -----------------------------
@router.post("/", response_model=Usuario)
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)) -> Usuario:
    """
    Crea un usuario y registra la acción en el historial.
    """
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    historial = Historial(
        entidad="Usuario",
        accion="CREAR",
        descripcion=f"Usuario '{usuario.nombre}' creado con id {usuario.idUsuario}",
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return usuario


# -----------------------------
# READ - LISTAR TODOS / FILTRAR
# -----------------------------
@router.get("/", response_model=List[Usuario])
def listar_usuarios(
    session: Session = Depends(get_session),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre (contiene)"),
    ingreso_min: Optional[float] = Query(None, description="Filtrar por ingreso mínimo"),
    ingreso_max: Optional[float] = Query(None, description="Filtrar por ingreso máximo"),
) -> List[Usuario]:
    """
    Lista todos los usuarios, con filtros opcionales por nombre e ingresos.
    """
    query = select(Usuario)

    if nombre:
        query = query.where(Usuario.nombre.contains(nombre))

    if ingreso_min is not None:
        query = query.where(Usuario.ingresos >= ingreso_min)

    if ingreso_max is not None:
        query = query.where(Usuario.ingresos <= ingreso_max)

    usuarios = session.exec(query).all()
    return usuarios


# -----------------------------
# READ - OBTENER POR ID
# -----------------------------
@router.get("/{usuario_id}", response_model=Usuario)
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)) -> Usuario:
    """
    Obtiene un usuario por su id.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# -----------------------------
# UPDATE COMPLETO (PUT)
# -----------------------------
@router.put("/{usuario_id}", response_model=Usuario)
def actualizar_usuario(
    usuario_id: int,
    datos: Usuario,
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Reemplaza completamente los datos de un usuario existente.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = datos.nombre
    usuario.ingresos = datos.ingresos
    usuario.gastos = datos.gastos
    usuario.correo = datos.correo
    usuario.telefono = datos.telefono

    session.commit()
    session.refresh(usuario)

    historial = Historial(
        entidad="Usuario",
        accion="ACTUALIZAR",
        descripcion=f"Usuario '{usuario.nombre}' (id {usuario.idUsuario}) actualizado",
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return usuario


# -----------------------------
# UPDATE PARCIAL (PATCH)
# -----------------------------
@router.patch("/{usuario_id}", response_model=Usuario)
def actualizar_usuario_parcial(
    usuario_id: int,
    nombre: Optional[str] = None,
    ingresos: Optional[float] = None,
    gastos: Optional[float] = None,
    correo: Optional[str] = None,
    telefono: Optional[str] = None,
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Actualiza parcialmente un usuario. Solo se modifican los campos enviados.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cambios = []

    if nombre is not None:
        usuario.nombre = nombre
        cambios.append("nombre")
    if ingresos is not None:
        usuario.ingresos = ingresos
        cambios.append("ingresos")
    if gastos is not None:
        usuario.gastos = gastos
        cambios.append("gastos")
    if correo is not None:
        usuario.correo = correo
        cambios.append("correo")
    if telefono is not None:
        usuario.telefono = telefono
        cambios.append("telefono")

    if cambios:
        session.commit()
        session.refresh(usuario)

        detalle_cambios = ", ".join(cambios)
        historial = Historial(
            entidad="Usuario",
            accion="ACTUALIZAR_PARCIAL",
            descripcion=f"Usuario '{usuario.nombre}' (id {usuario.idUsuario}) actualizado parcialmente. Campos: {detalle_cambios}",
            fecha=datetime.now(),
        )
        session.add(historial)
        session.commit()

    return usuario


# -----------------------------
# DELETE
# -----------------------------
@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Elimina un usuario y registra la acción en el historial.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    historial = Historial(
        entidad="Usuario",
        accion="ELIMINAR",
        descripcion=f"Usuario '{usuario.nombre}' (id {usuario.idUsuario}) eliminado",
        fecha=datetime.now(),
    )
    session.add(historial)
    session.delete(usuario)
    session.commit()

    return {"mensaje": "Usuario eliminado correctamente y registrado en historial"}