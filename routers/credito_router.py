from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from models.credito import Credito
from models.usuario import Usuario
from models.historial import Historial

router = APIRouter(prefix="/creditos", tags=["Créditos"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
def ver_creditos(request: Request, session: Session = Depends(get_session)):
    creditos = session.exec(select(Credito)).all()
    return templates.TemplateResponse("creditos.html", {"request": request, "creditos": creditos})


@router.post("/crear")
def crear_credito(credito: Credito, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, credito.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no existe")

    session.add(credito)
    session.commit()
    session.refresh(credito)

    historial = Historial(
        accion="CREAR",
        detalle=f"Crédito creado para usuario {usuario.nombre}",
        usuario_id=usuario.id
    )
    session.add(historial)
    session.commit()

    return credito


@router.get("/usuario")
def buscar_creditos_por_usuario(nombre: str, session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario).where(Usuario.nombre.contains(nombre))).all()
    resultado = []

    for u in usuarios:
        creditos = session.exec(select(Credito).where(Credito.usuario_id == u.id)).all()
        resultado.append({"usuario": u.nombre, "creditos": creditos})

    return resultado


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


@router.delete("/{credito_id}")
def eliminar_credito(credito_id: int, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    historial = Historial(
        accion="ELIMINAR",
        detalle=f"Crédito {credito.id} eliminado",
        usuario_id=credito.usuario_id
    )
    session.add(historial)

    session.delete(credito)
    session.commit()

    return {"mensaje": "Crédito eliminado"}
