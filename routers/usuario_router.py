from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from models.usuario import Usuario
from models.historial import Historial

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
templates = Jinja2Templates(directory="templates")


# ---------------- HTML ----------------
@router.get("/")
def ver_usuarios(request: Request, session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario)).all()
    return templates.TemplateResponse("usuarios.html", {"request": request, "usuarios": usuarios})


# ---------------- API CRUD ----------------
@router.post("/crear")
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    # Guardar en historial
    historial = Historial(
        accion="CREAR",
        detalle=f"Usuario {usuario.nombre} creado",
        usuario_id=usuario.id
    )
    session.add(historial)
    session.commit()

    return usuario


@router.get("/buscar")
def buscar_usuario(nombre: str, session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.nombre.contains(nombre))).all()
    return usuarios


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: int, datos: Usuario, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = datos.nombre
    usuario.ingresos = datos.ingresos
    usuario.gastos = datos.gastos

    session.commit()
    session.refresh(usuario)

    historial = Historial(
        accion="ACTUALIZAR",
        detalle=f"Usuario {usuario.nombre} actualizado",
        usuario_id=usuario.id
    )
    session.add(historial)
    session.commit()

    return usuario


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    historial = Historial(
        accion="ELIMINAR",
        detalle=f"Usuario {usuario.nombre} eliminado",
        usuario_id=usuario.id
    )
    session.add(historial)

    session.delete(usuario)
    session.commit()

    return {"mensaje": "Usuario eliminado y registrado en historial"}
