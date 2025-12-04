# routers/usuario_router.py

import os
import uuid
from datetime import datetime
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    File,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from database import get_session
from models.usuario import Usuario
from models.historial import Historial

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# -----------------------------
# LISTAR (API JSON)
# -----------------------------
@router.get("/", response_model=List[Usuario])
def listar_usuarios(session: Session = Depends(get_session)):
    return session.exec(select(Usuario)).all()


# -----------------------------
# CREAR DESDE FORMULARIO (HTML)
# -----------------------------
@router.post("/crear")
def crear_usuario_form(
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    cedula: UploadFile | None = File(None),
    session: Session = Depends(get_session),
):
    # Guardar archivo de cédula (si viene)
    cedula_path: str | None = None
    if cedula and cedula.filename:
        _, ext = os.path.splitext(cedula.filename)
        ext = ext.lower()
        if ext not in [".pdf", ".jpg", ".jpeg"]:
            raise HTTPException(
                status_code=400,
                detail="La cédula debe ser un archivo PDF o JPG",
            )

        upload_dir = "upload/cedulas"
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(cedula.file.read())

        cedula_path = file_path

    usuario = Usuario(
        nombre=nombre,
        ingresos=ingresos,
        gastos=gastos,
        correo=correo,
        telefono=telefono,
        cedula=cedula_path,
    )
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

    # Regresar a la vista HTML
    return RedirectResponse(url="/ui/usuarios", status_code=303)


# -----------------------------
# ACTUALIZAR DESDE FORMULARIO (HTML)
# -----------------------------
@router.post("/actualizar/{usuario_id}")
def actualizar_usuario_form(
    usuario_id: int,
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    cedula: UploadFile | None = File(None),
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = nombre
    usuario.ingresos = ingresos
    usuario.gastos = gastos
    usuario.correo = correo
    usuario.telefono = telefono

    # Si viene una nueva cédula, la guardamos y reemplazamos la ruta anterior
    if cedula and cedula.filename:
        _, ext = os.path.splitext(cedula.filename)
        ext = ext.lower()
        if ext not in [".pdf", ".jpg", ".jpeg"]:
            raise HTTPException(
                status_code=400,
                detail="La cédula debe ser un archivo PDF o JPG",
            )

        upload_dir = "upload/cedulas"
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(cedula.file.read())

        usuario.cedula = file_path

    session.commit()
    session.refresh(usuario)

    historial = Historial(
        entidad="Usuario",
        accion="ACTUALIZAR",
        descripcion=f"Usuario id {usuario.idUsuario} actualizado",
        fecha=datetime.now(),
    )
    session.add(historial)
    session.commit()

    return RedirectResponse(url="/ui/usuarios", status_code=303)