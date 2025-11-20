from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models.categoria import Categoria

router = APIRouter(prefix="/categorias", tags=["Categorías"])

# CREATE
@router.post("/")
def crear_categoria(categoria: Categoria, session: Session = Depends(get_session)):
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

# READ ALL
@router.get("/")
def listar_categorias(session: Session = Depends(get_session)):
    return session.exec(select(Categoria)).all()

# READ ONE
@router.get("/{categoria_id}")
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

# UPDATE
@router.put("/{categoria_id}")
def actualizar_categoria(categoria_id: int, datos: Categoria, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    categoria.nombre = datos.nombre
    session.commit()
    session.refresh(categoria)
    return categoria

# PATCH
@router.patch("/{categoria_id}")
def patch_categoria(categoria_id: int, datos: dict, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, value in datos.items():
        if hasattr(categoria, key):
            setattr(categoria, key, value)
    session.commit()
    session.refresh(categoria)
    return categoria

# DELETE
@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    session.delete(categoria)
    session.commit()
    return {"mensaje": "Categoría eliminada correctamente"}
