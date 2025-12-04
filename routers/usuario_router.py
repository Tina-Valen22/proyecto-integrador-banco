from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from database import get_session
from models.usuario import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ---------------------------
# Endpoints JSON (API REST)
# ---------------------------

@router.get("/", response_model=List[Usuario])
def listar_usuarios(session: Session = Depends(get_session)):
    return session.exec(select(Usuario)).all()


@router.get("/{usuario_id}", response_model=Usuario)
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def crear_usuario_api(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.put("/{usuario_id}", response_model=Usuario)
def actualizar_usuario_api(
    usuario_id: int,
    datos: Usuario,
    session: Session = Depends(get_session),
):
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario_db.nombre = datos.nombre
    usuario_db.ingresos = datos.ingresos
    usuario_db.gastos = datos.gastos
    usuario_db.correo = datos.correo
    usuario_db.telefono = datos.telefono

    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(usuario)
    session.commit()
    return None


# -----------------------------------------
# Endpoints para formularios HTML (UI)
# -----------------------------------------

@router.post("/crear")
def crear_usuario_form(
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    correo: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    usuario = Usuario(
        nombre=nombre,
        ingresos=ingresos,
        gastos=gastos,
        correo=correo,
        telefono=telefono,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    # Volver a la página HTML de usuarios
    return RedirectResponse(url="/ui/usuarios", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/actualizar")
def actualizar_usuario_form(
    idUsuario: int = Form(...),
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    correo: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, idUsuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = nombre
    usuario.ingresos = ingresos
    usuario.gastos = gastos
    usuario.correo = correo
    usuario.telefono = telefono

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return RedirectResponse(url="/ui/usuarios", status_code=status.HTTP_303_SEE_OTHER)