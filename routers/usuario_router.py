from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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
    return templates.TemplateResponse("usuarios.html", {
        "request": request,
        "usuarios": usuarios
    })


# ---------------- API CRUD ----------------
@router.post("/crear")
def crear_usuario(
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    session: Session = Depends(get_session)
):
    usuario = Usuario(nombre=nombre, ingresos=ingresos, gastos=gastos)
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

    return RedirectResponse(url="/usuarios", status_code=303)


@router.get("/buscar")
def buscar_usuario(nombre: str, session: Session = Depends(get_session)):
    usuarios = session.exec(
        select(Usuario).where(Usuario.nombre.contains(nombre))
    ).all()
    return usuarios


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/actualizar/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = nombre
    usuario.ingresos = ingresos
    usuario.gastos = gastos

    session.commit()
    session.refresh(usuario)

    historial = Historial(
        accion="ACTUALIZAR",
        detalle=f"Usuario {usuario.nombre} actualizado",
        usuario_id=usuario.id
    )
    session.add(historial)
    session.commit()

    return RedirectResponse(url="/usuarios", status_code=303)


@router.post("/eliminar/{usuario_id}")
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

    return RedirectResponse(url="/usuarios", status_code=303)
