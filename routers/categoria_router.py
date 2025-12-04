# routers/categoria_router.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Form, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from database import get_session
from models.categoria import Categoria
from models.credito import Credito
from models.credito_categoria import CreditoCategoria
from models.historial import Historial

router = APIRouter(prefix="/categorias", tags=["Categorías"])


# -----------------------------
# CREATE (API JSON)
# -----------------------------
@router.post("/", response_model=Categoria)
def crear_categoria(
    categoria: Categoria,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Crea una categoría y registra la acción en el historial.
    """
    # Validar duplicado por nombre
    existente = session.exec(
        select(Categoria).where(Categoria.nombre == categoria.nombre)
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una categoría con el nombre '{categoria.nombre}'",
        )

    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    h = Historial(
        entidad="Categoría",
        accion="CREAR",
        descripcion=f"Categoría '{categoria.nombre}' creada con id {categoria.idCategoria}",
        fecha=datetime.now(),
    )
    session.add(h)
    session.commit()

    return categoria


# -----------------------------
# READ - LISTAR / FILTRAR (API JSON)
# -----------------------------
@router.get("/", response_model=List[Categoria])
def listar_categorias(
    session: Session = Depends(get_session),
    nombre: Optional[str] = Query(
        None, description="Filtrar por nombre (contiene)"
    ),
) -> List[Categoria]:
    """
    Lista todas las categorías, con filtro opcional por nombre.
    """
    query = select(Categoria)

    if nombre:
        query = query.where(Categoria.nombre.contains(nombre))

    categorias = session.exec(query).all()
    return categorias


# -----------------------------
# READ - OBTENER POR ID (API JSON)
# -----------------------------
@router.get("/{categoria_id}", response_model=Categoria)
def obtener_categoria(
    categoria_id: int,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Obtiene una categoría por su id.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


# -----------------------------
# UPDATE COMPLETO (PUT, API JSON)
# -----------------------------
@router.put("/{categoria_id}", response_model=Categoria)
def actualizar_categoria(
    categoria_id: int,
    datos: Categoria,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Reemplaza completamente los datos de una categoría.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Validar nombre duplicado si cambia
    if datos.nombre != categoria.nombre:
        existente = session.exec(
            select(Categoria).where(Categoria.nombre == datos.nombre)
        ).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{datos.nombre}'",
            )

    categoria.nombre = datos.nombre
    categoria.descripcion = datos.descripcion

    session.commit()
    session.refresh(categoria)

    h = Historial(
        entidad="Categoría",
        accion="ACTUALIZAR",
        descripcion=(
            f"Categoría id {categoria.idCategoria} actualizada "
            f"('{categoria.nombre}')"
        ),
        fecha=datetime.now(),
    )
    session.add(h)
    session.commit()

    return categoria


# -----------------------------
# UPDATE PARCIAL (PATCH, API JSON)
# -----------------------------
@router.patch("/{categoria_id}", response_model=Categoria)
def actualizar_categoria_parcial(
    categoria_id: int,
    nombre: Optional[str] = None,
    descripcion: Optional[str] = None,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Actualiza parcialmente una categoría. Solo se modifican los campos enviados.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    cambios = []

    if nombre is not None and nombre != categoria.nombre:
        existente = session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{nombre}'",
            )
        categoria.nombre = nombre
        cambios.append("nombre")

    if descripcion is not None:
        categoria.descripcion = descripcion
        cambios.append("descripcion")

    if cambios:
        session.commit()
        session.refresh(categoria)

        detalle_cambios = ", ".join(cambios)
        h = Historial(
            entidad="Categoría",
            accion="ACTUALIZAR_PARCIAL",
            descripcion=(
                f"Categoría id {categoria.idCategoria} actualizada parcialmente. "
                f"Campos modificados: {detalle_cambios}"
            ),
            fecha=datetime.now(),
        )
        session.add(h)
        session.commit()

    return categoria


# -----------------------------
# DELETE (API JSON)
# -----------------------------
@router.delete("/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina una categoría, sus relaciones con créditos,
    y registra la acción en el historial.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Eliminar relaciones en la tabla intermedia
    relaciones = session.exec(
        select(CreditoCategoria).where(CreditoCategoria.categoria_id == categoria_id)
    ).all()
    for rel in relaciones:
        session.delete(rel)

    h = Historial(
        entidad="Categoría",
        accion="ELIMINAR",
        descripcion=f"Categoría '{categoria.nombre}' (id {categoria.idCategoria}) eliminada",
        fecha=datetime.now(),
    )
    session.add(h)

    session.delete(categoria)
    session.commit()

    return {"mensaje": "Categoría y relaciones asociadas eliminadas correctamente"}


# -----------------------------
# ASIGNAR CATEGORÍA A CRÉDITO (API JSON)
# -----------------------------
@router.post("/{categoria_id}/creditos/{credito_id}")
def asignar_categoria_a_credito(
    categoria_id: int,
    credito_id: int,
    session: Session = Depends(get_session),
):
    """
    Asocia una categoría a un crédito (relación N:M).
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    # Verificar si ya existe la relación
    existente = session.exec(
        select(CreditoCategoria).where(
            CreditoCategoria.categoria_id == categoria_id,
            CreditoCategoria.credito_id == credito_id,
        )
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="La categoría ya está asociada a este crédito",
        )

    relacion = CreditoCategoria(
        categoria_id=categoria_id,
        credito_id=credito_id,
    )
    session.add(relacion)

    h = Historial(
        entidad="Categoría-Crédito",
        accion="ASIGNAR",
        descripcion=(
            f"Categoría '{categoria.nombre}' (id {categoria.idCategoria}) "
            f"asignada al crédito id {credito.idCredito}"
        ),
        fecha=datetime.now(),
    )
    session.add(h)

    session.commit()

    return {"mensaje": "Categoría asignada al crédito correctamente"}


# -----------------------------
# QUITAR CATEGORÍA DE CRÉDITO (API JSON)
# -----------------------------
@router.delete("/{categoria_id}/creditos/{credito_id}")
def quitar_categoria_de_credito(
    categoria_id: int,
    credito_id: int,
    session: Session = Depends(get_session),
):
    """
    Elimina la asociación de una categoría con un crédito.
    """
    relacion = session.exec(
        select(CreditoCategoria).where(
            CreditoCategoria.categoria_id == categoria_id,
            CreditoCategoria.credito_id == credito_id,
        )
    ).first()

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="La relación categoría-crédito no existe",
        )

    categoria = session.get(Categoria, categoria_id)
    credito = session.get(Credito, credito_id)

    h = Historial(
        entidad="Categoría-Crédito",
        accion="DESASIGNAR",
        descripcion=(
            f"Categoría '{categoria.nombre}' (id {categoria.idCategoria}) "
            f"desasignada del crédito id {credito.idCredito}"
        ),
        fecha=datetime.now(),
    )
    session.add(h)

    session.delete(relacion)
    session.commit()

    return {"mensaje": "Categoría desasignada del crédito correctamente"}


# -----------------------------------------
# Endpoints para formularios HTML (UI)
# -----------------------------------------

@router.post("/crear")
def crear_categoria_form(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    """
    Crea una categoría desde el formulario HTML, la asocia a un crédito
    y redirige a /ui/categorias.
    Todos los campos son obligatorios.
    """
    if not nombre.strip() or not descripcion.strip():
        raise HTTPException(
            status_code=400,
            detail="Nombre y descripción son obligatorios",
        )

    # Validar crédito
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(
            status_code=400,
            detail="El crédito seleccionado no existe",
        )

    # Validar duplicado por nombre
    existente = session.exec(
        select(Categoria).where(Categoria.nombre == nombre.strip())
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una categoría con el nombre '{nombre.strip()}'",
        )

    categoria = Categoria(
        nombre=nombre.strip(),
        descripcion=descripcion.strip(),
    )
    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    # Crear relación con el crédito
    relacion = CreditoCategoria(
        categoria_id=categoria.idCategoria,
        credito_id=credito_id,
    )
    session.add(relacion)

    h_cat = Historial(
        entidad="Categoría",
        accion="CREAR",
        descripcion=f"Categoría '{categoria.nombre}' creada con id {categoria.idCategoria}",
        fecha=datetime.now(),
    )
    session.add(h_cat)

    h_rel = Historial(
        entidad="Categoría-Crédito",
        accion="ASIGNAR",
        descripcion=(
            f"Categoría '{categoria.nombre}' (id {categoria.idCategoria}) "
            f"asignada al crédito id {credito.idCredito}"
        ),
        fecha=datetime.now(),
    )
    session.add(h_rel)

    session.commit()

    return RedirectResponse(url="/ui/categorias", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/actualizar")
def actualizar_categoria_form(
    idCategoria: int = Form(...),
    nombre: str = Form(...),
    descripcion: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    """
    Actualiza una categoría desde el formulario HTML,
    ajusta su asociación con un crédito
    y redirige a /ui/categorias.
    Todos los campos son obligatorios.
    """
    categoria = session.get(Categoria, idCategoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if not nombre.strip() or not descripcion.strip():
        raise HTTPException(
            status_code=400,
            detail="Nombre y descripción son obligatorios",
        )

    # Validar crédito
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(
            status_code=400,
            detail="El crédito seleccionado no existe",
        )

    # Validar nombre duplicado si cambia
    if nombre.strip() != categoria.nombre:
        existente = session.exec(
            select(Categoria).where(Categoria.nombre == nombre.strip())
        ).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{nombre.strip()}'",
            )

    categoria.nombre = nombre.strip()
    categoria.descripcion = descripcion.strip()
    session.add(categoria)

    # Ajustar relaciones: dejamos solo el crédito seleccionado
    relaciones = session.exec(
        select(CreditoCategoria).where(CreditoCategoria.categoria_id == idCategoria)
    ).all()
    for rel in relaciones:
        session.delete(rel)

    nueva_relacion = CreditoCategoria(
        categoria_id=idCategoria,
        credito_id=credito_id,
    )
    session.add(nueva_relacion)

    h = Historial(
        entidad="Categoría",
        accion="ACTUALIZAR",
        descripcion=(
            f"Categoría id {categoria.idCategoria} actualizada "
            f"('{categoria.nombre}') y asociada al crédito id {credito.idCredito}"
        ),
        fecha=datetime.now(),
    )
    session.add(h)

    session.commit()

    return RedirectResponse(url="/ui/categorias", status_code=status.HTTP_303_SEE_OTHER)