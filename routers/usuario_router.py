from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import engine
from models.usuario import Usuario
from models.historial import Historial
from datetime import datetime

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/")
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.get("/")
def listar_usuarios(session: Session = Depends(get_session)):
    return session.exec(select(Usuario)).all()

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
    return usuario

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    historial = Historial(
        entidad="Usuario",
        accion="ELIMINAR",
        descripcion=f"Usuario '{usuario.nombre}' eliminado",
        fecha=datetime.now()
    )
    session.add(historial)
    session.delete(usuario)
    session.commit()
    return {"mensaje": "Usuario eliminado correctamente y registrado en historial"}
