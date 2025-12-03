# routers/categoria_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from database import get_session
from models.categoria import Categoria
from models.credito_categoria import CreditoCategoria
from models.credito import Credito
from models.historial import Historial

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/")
def ver_categorias(request: Request, session: Session = Depends(get_session)):
    categorias = session.exec(select(Categoria)).all()
    creditos = session.exec(select(Credito)).all()
    return templates.TemplateResponse("categorias.html",
        {"request": request, "categorias": categorias, "creditos": creditos}
    )


@router.post("/crear")
def crear_categoria(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    session: Session = Depends(get_session)
):
    categoria = Categoria(nombre=nombre, descripcion=descripcion)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    h = Historial(
        accion="CREAR",
        detalle=f"Categoría '{categoria.nombre}' creada",
        usuario_id=None
    )

    session.add(h)
    session.commit()

    return RedirectResponse(url="/categorias", status_code=303)


@router.post("/vincular")
def vincular_credito_categoria(
    credito_id: int = Form(...),
    categoria_id: int = Form(...),
    session: Session = Depends(get_session)
):
    credito = session.get(Credito, credito_id)
    categoria = session.get(Categoria, categoria_id)

    if not credito or not categoria:
        raise HTTPException(status_code=404, detail="Crédito o Categoría no encontrados")

    link = CreditoCategoria(credito_id=credito_id, categoria_id=categoria_id)
    session.add(link)
    session.commit()

    h = Historial(
        accion="VINCULAR",
        detalle=f"Crédito {credito_id} vinculado a categoría {categoria.nombre}",
        usuario_id=credito.usuario_id
    )

    session.add(h)
    session.commit()

    return RedirectResponse(url="/categorias", status_code=303)


@router.post("/eliminar/{categoria_id}")
def eliminar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    h = Historial(
        accion="ELIMINAR",
        detalle=f"Categoría '{categoria.nombre}' eliminada",
        usuario_id=None
    )

    session.add(h)
    session.delete(categoria)
    session.commit()

    return RedirectResponse(url="/categorias", status_code=303)
