from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from database import engine
from models.credito import Credito
from models.usuario import Usuario
from models.historial import Historial
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/creditos", tags=["Créditos"])

# Generar sesión
def get_session():
    with Session(engine) as session:
        yield session

# ✅ Crear un crédito asignado a un usuario (por nombre o ID)
@router.post("/")
def crear_credito(
    monto: float,
    plazo: int,
    tipo: str,
    usuario_nombre: Optional[str] = None,
    usuario_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    # Buscar usuario por nombre o ID
    usuario = None
    if usuario_nombre:
        usuario = session.exec(select(Usuario).where(Usuario.nombre == usuario_nombre)).first()
    elif usuario_id:
        usuario = session.get(Usuario, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    credito = Credito(
        monto=monto,
        plazo=plazo,
        tipo=tipo,
        usuario_id=usuario.idUsuario
    )

    session.add(credito)
    session.commit()
    session.refresh(credito)

    # Registrar acción en historial
    historial = Historial(
        entidad="Crédito",
        accion="CREAR",
        descripcion=f"Crédito creado para usuario '{usuario.nombre}'",
        fecha=datetime.now()
    )
    session.add(historial)
    session.commit()

    return {"mensaje": "Crédito creado exitosamente", "credito": credito}

# ✅ Listar todos los créditos
@router.get("/", response_model=List[Credito])
def listar_creditos(session: Session = Depends(get_session)):
    return session.exec(select(Credito)).all()

# ✅ Buscar créditos por nombre de usuario
@router.get("/buscar_por_usuario/")
def buscar_creditos_por_usuario(nombre: str = Query(..., description="Nombre del usuario"), session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.nombre == nombre)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    creditos = session.exec(select(Credito).where(Credito.usuario_id == usuario.idUsuario)).all()
    if not creditos:
        raise HTTPException(status_code=404, detail=f"No hay créditos registrados para {nombre}")
    return {"usuario": usuario.nombre, "creditos": creditos}

# ✅ Obtener crédito por ID
@router.get("/{credito_id}")
def obtener_credito(credito_id: int, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    return credito

# ✅ Actualizar crédito
@router.put("/{credito_id}")
def actualizar_credito(credito_id: int, datos: Credito, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    credito.monto = datos.monto
    credito.plazo = datos.plazo
    credito.tipo = datos.tipo
    session.commit()
    session.refresh(credito)
    return credito

# ✅ Eliminar crédito y registrar en historial
@router.delete("/{credito_id}")
def eliminar_credito(credito_id: int, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    usuario = session.get(Usuario, credito.usuario_id)

    historial = Historial(
        entidad="Crédito",
        accion="ELIMINAR",
        descripcion=f"Crédito {credito.idCredito} eliminado del usuario '{usuario.nombre if usuario else 'Desconocido'}'",
        fecha=datetime.now()
    )
    session.add(historial)
    session.delete(credito)
    session.commit()
    return {"mensaje": "Crédito eliminado y registrado en historial"}
