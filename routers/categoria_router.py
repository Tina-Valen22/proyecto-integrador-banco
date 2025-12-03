# routers/categoria_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
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
    return templates.TemplateResponse("categorias.html", {"request": request, "categorias": categorias})

@router.post("/crear")
def crear_categoria(categoria: Categoria, session: Session = Depends(get_session)):
    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    h = Historial(accion="CREAR", detalle=f"Categoría '{categoria.nombre}' creada", usuario_id=None)
    session.add(h)
    session.commit()
    return categoria

@router.get("/{categoria_id}")
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    cat = session.get(Categoria, categoria_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat

@router.post("/vincular")
def vincular_credito_categoria(credito_id: int, categoria_id: int, session: Session = Depends(get_session)):
    credito = session.get(Credito, credito_id)
    cat = session.get(Categoria, categoria_id)
    if not credito or not cat:
        raise HTTPException(status_code=404, detail="Crédito o Categoría no encontrados")

    link = CreditoCategoria(credito_id=credito_id, categoria_id=categoria_id)
    session.add(link)
    session.commit()
    session.refresh(link)

    h = Historial(accion="VINCULAR", detalle=f"Crédito {credito_id} vinculado a categoría '{cat.nombre}'", usuario_id=credito.usuario_id)
    session.add(h)
    session.commit()
    return {"mensaje": "Vinculado correctamente", "link": link}

@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    cat = session.get(Categoria, categoria_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    h = Historial(accion="ELIMINAR", detalle=f"Categoría '{cat.nombre}' eliminada", usuario_id=None)
    session.add(h)

    session.delete(cat)
    session.commit()
    return {"mensaje": "Categoría eliminada"}
