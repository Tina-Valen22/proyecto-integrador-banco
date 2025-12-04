import os
import shutil
import uuid
from fastapi import UploadFile, File
from fastapi import (
    FastAPI,
    Request,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlmodel import Session, select

from database import create_db_and_tables, get_session

# Routers (API JSON)
from routers import (
    usuario_router,
    credito_router,
    interes_router,
    categoria_router,
    simulacion_router,
    reporte_router,
    historial_router,
)

# Modelos
from models.usuario import Usuario
from models.credito import Credito
from models.categoria import Categoria
from models.credito_categoria import CreditoCategoria
from models.interes import Interes
from models.simulacion import Simulacion
from models.reporte import Reporte
from models.historial import Historial


# -----------------------------
# Inicialización de la app
# -----------------------------
app = FastAPI(
    title="API Integrador Banco",
    description="Proyecto integrador de banco con FastAPI y SQLModel",
    version="1.0.0",
)


# -----------------------------
# Crear carpeta upload si no existe, crear carpeta upload
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "upload")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, "cedulas"), exist_ok=True)  

# -----------------------------
# Templates y archivos estáticos, creador de la carpeta upload 
# -----------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/upload", StaticFiles(directory="upload"), name="upload")
templates = Jinja2Templates(directory="templates")


# -----------------------------
# Eventos de ciclo de vida
# -----------------------------
@app.on_event("startup")
def on_startup():
    """
    Evento de arranque de la aplicación.
    Crea la base de datos y las tablas, y carga datos iniciales si es necesario.
    """
    create_db_and_tables()


# -----------------------------
# Rutas base (vista HTML)
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    # Pantalla de inicio en home.html
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/health")
def health_check():
    """
    Endpoint simple de salud para verificar que la API está arriba.
    """
    return {"status": "ok", "message": "API Integrador Banco funcionando"}


# ============================================================
# RUTAS UI (HTML) - USUARIOS
# ============================================================

@app.get("/ui/usuarios", response_class=HTMLResponse)
def ui_usuarios(
    request: Request,
    session: Session = Depends(get_session),
):
    usuarios = session.exec(select(Usuario)).all()
    return templates.TemplateResponse(
        "usuarios.html",
        {
            "request": request,
            "usuarios": usuarios,
            "usuario_editar": None,
            "form_action": "/ui/usuarios/crear",
            "titulo_form": "Crear usuario",
        },
    )


@app.get("/ui/usuarios/{usuario_id}", response_class=HTMLResponse)
def ui_usuarios_editar(
    usuario_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    usuarios = session.exec(select(Usuario)).all()
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return templates.TemplateResponse(
        "usuarios.html",
        {
            "request": request,
            "usuarios": usuarios,
            "usuario_editar": usuario,
            "form_action": f"/ui/usuarios/{usuario_id}/actualizar",
            "titulo_form": "Editar usuario",
        },
    )


@app.post("/ui/usuarios/crear")
def ui_usuarios_crear(
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    cedula: UploadFile = File(None),
    session: Session = Depends(get_session),
):
    # 1. Lógica para guardar el archivo (si se subió uno)
    ruta_para_bd = None
    
    if cedula and cedula.filename:
        # Validar extensión
        ext = os.path.splitext(cedula.filename)[1].lower()
        if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
             raise HTTPException(status_code=400, detail="Solo archivos PDF o JPG")
        
        # Generar nombre único para el disco (evita conflictos)
        nombre_archivo = f"{uuid.uuid4().hex}{ext}"
        
        # Ruta física donde se guarda (depende de tu SO)
        ruta_fisica = os.path.join(UPLOADS_DIR, "cedulas", nombre_archivo)
        
        # Guardar en disco
        with open(ruta_fisica, "wb") as buffer:
            shutil.copyfileobj(cedula.file, buffer)
            
        # IMPORTANTE: Guardamos la ruta relativa con "/" para que funcione como URL web
        # Ejemplo: upload/cedulas/archivo.jpg
        ruta_para_bd = f"upload/cedulas/{nombre_archivo}"

    # 2. Crear usuario
    usuario = Usuario(
        nombre=nombre,
        ingresos=ingresos,
        gastos=gastos,
        correo=correo,
        telefono=telefono,
        cedula=ruta_para_bd, # Guardamos la ruta web
    )
    session.add(usuario)
    session.commit()

    return RedirectResponse(url="/ui/usuarios", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/ui/usuarios/{usuario_id}/actualizar")
def ui_usuarios_actualizar(
    usuario_id: int,
    nombre: str = Form(...),
    ingresos: float = Form(...),
    gastos: float = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    cedula: UploadFile = File(None),
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = nombre
    usuario.ingresos = ingresos
    usuario.gastos = gastos
    usuario.correo = correo
    usuario.telefono = telefono

    # Si suben un nuevo archivo, lo procesamos
    if cedula and cedula.filename:
        ext = os.path.splitext(cedula.filename)[1].lower()
        if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
             raise HTTPException(status_code=400, detail="Solo archivos PDF o JPG")
        
        nombre_archivo = f"{uuid.uuid4().hex}{ext}"
        ruta_fisica = os.path.join(UPLOADS_DIR, "cedulas", nombre_archivo)
        
        with open(ruta_fisica, "wb") as buffer:
            shutil.copyfileobj(cedula.file, buffer)
            
        # Actualizamos el campo en la BD
        usuario.cedula = f"upload/cedulas/{nombre_archivo}"

    session.commit()

    return RedirectResponse(url="/ui/usuarios", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================
# RUTAS UI (HTML) - CRÉDITOS
# ============================================================

@app.get("/ui/creditos", response_class=HTMLResponse)
def ui_creditos(
    request: Request,
    session: Session = Depends(get_session),
):
    creditos = session.exec(select(Credito)).all()
    usuarios = session.exec(select(Usuario)).all()
    return templates.TemplateResponse(
        "creditos.html",
        {
            "request": request,
            "creditos": creditos,
            "usuarios": usuarios,
            "credito_editar": None,
            "form_action": "/ui/creditos/crear",
            "titulo_form": "Crear crédito",
        },
    )


@app.get("/ui/creditos/{credito_id}", response_class=HTMLResponse)
def ui_creditos_editar(
    credito_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    creditos = session.exec(select(Credito)).all()
    usuarios = session.exec(select(Usuario)).all()
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    return templates.TemplateResponse(
        "creditos.html",
        {
            "request": request,
            "creditos": creditos,
            "usuarios": usuarios,
            "credito_editar": credito,
            "form_action": f"/ui/creditos/{credito_id}/actualizar",
            "titulo_form": "Editar crédito",
        },
    )


@app.post("/ui/creditos/crear")
def ui_creditos_crear(
    usuario_id: int = Form(...),
    monto: float = Form(...),
    plazo: int = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(...),
    session: Session = Depends(get_session),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    credito = Credito(
        usuario_id=usuario_id,
        monto=monto,
        plazo=plazo,
        tipo=tipo,
        descripcion=descripcion,
    )
    session.add(credito)
    session.commit()

    return RedirectResponse(url="/ui/creditos", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/ui/creditos/{credito_id}/actualizar")
def ui_creditos_actualizar(
    credito_id: int,
    usuario_id: int = Form(...),
    monto: float = Form(...),
    plazo: int = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(...),
    session: Session = Depends(get_session),
):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    credito.usuario_id = usuario_id
    credito.monto = monto
    credito.plazo = plazo
    credito.tipo = tipo
    credito.descripcion = descripcion

    session.commit()

    return RedirectResponse(url="/ui/creditos", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================
# RUTAS UI (HTML) - CATEGORÍAS
# ============================================================

@app.get("/ui/categorias", response_class=HTMLResponse)
def ui_categorias(
    request: Request,
    session: Session = Depends(get_session),
):
    categorias = session.exec(select(Categoria)).all()
    creditos = session.exec(select(Credito)).all()
    relaciones = session.exec(select(CreditoCategoria)).all()

    # Mapeo categoria_id -> primer credito_id asociado
    cat_creditos = {}
    for rel in relaciones:
        if rel.categoria_id not in cat_creditos:
            cat_creditos[rel.categoria_id] = rel.credito_id

    return templates.TemplateResponse(
        "categorias.html",
        {
            "request": request,
            "categorias": categorias,
            "creditos": creditos,
            "cat_creditos": cat_creditos,
            "categoria_editar": None,
            "form_action": "/ui/categorias/crear",
            "titulo_form": "Crear categoría",
        },
    )


@app.get("/ui/categorias/{categoria_id}", response_class=HTMLResponse)
def ui_categorias_editar(
    categoria_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    categorias = session.exec(select(Categoria)).all()
    creditos = session.exec(select(Credito)).all()
    relaciones = session.exec(select(CreditoCategoria)).all()

    cat_creditos = {}
    for rel in relaciones:
        if rel.categoria_id not in cat_creditos:
            cat_creditos[rel.categoria_id] = rel.credito_id

    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return templates.TemplateResponse(
        "categorias.html",
        {
            "request": request,
            "categorias": categorias,
            "creditos": creditos,
            "cat_creditos": cat_creditos,
            "categoria_editar": categoria,
            "form_action": f"/ui/categorias/{categoria_id}/actualizar",
            "titulo_form": "Editar categoría",
        },
    )


@app.post("/ui/categorias/crear")
def ui_categorias_crear(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    categoria = Categoria(nombre=nombre, descripcion=descripcion)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    # Asociar categoría a crédito
    credito = session.get(Credito, credito_id)
    if credito:
        relacion = CreditoCategoria(
            categoria_id=categoria.idCategoria,
            credito_id=credito_id,
        )
        session.add(relacion)
        session.commit()

    return RedirectResponse(url="/ui/categorias", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/ui/categorias/{categoria_id}/actualizar")
def ui_categorias_actualizar(
    categoria_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    categoria.nombre = nombre
    categoria.descripcion = descripcion
    session.commit()
    session.refresh(categoria)

    # Actualizar relación con crédito (dejamos una sola por simplicidad)
    relaciones = session.exec(
        select(CreditoCategoria).where(CreditoCategoria.categoria_id == categoria_id)
    ).all()
    for rel in relaciones:
        session.delete(rel)
    session.commit()

    credito = session.get(Credito, credito_id)
    if credito:
        nueva_relacion = CreditoCategoria(
            categoria_id=categoria_id,
            credito_id=credito_id,
        )
        session.add(nueva_relacion)
        session.commit()

    return RedirectResponse(url="/ui/categorias", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================
# RUTAS UI (HTML) - INTERESES
# ============================================================

@app.get("/ui/intereses", response_class=HTMLResponse)
def ui_intereses(
    request: Request,
    session: Session = Depends(get_session),
):
    intereses = session.exec(select(Interes)).all()
    creditos = session.exec(select(Credito)).all()
    return templates.TemplateResponse(
        "intereses.html",
        {
            "request": request,
            "intereses": intereses,
            "creditos": creditos,
            "interes_editar": None,
            "form_action": "/ui/intereses/crear",
            "titulo_form": "Crear interés",
        },
    )


@app.get("/ui/intereses/{interes_id}", response_class=HTMLResponse)
def ui_intereses_editar(
    interes_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    intereses = session.exec(select(Interes)).all()
    creditos = session.exec(select(Credito)).all()
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    return templates.TemplateResponse(
        "intereses.html",
        {
            "request": request,
            "intereses": intereses,
            "creditos": creditos,
            "interes_editar": interes,
            "form_action": f"/ui/intereses/{interes_id}/actualizar",
            "titulo_form": "Editar interés",
        },
    )


@app.post("/ui/intereses/crear")
def ui_intereses_crear(
    tasa: float = Form(...),
    tipo: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=400, detail="Crédito no existe")

    interes = Interes(
        tasa=tasa,
        tipo=tipo,
        credito_id=credito_id,
    )
    session.add(interes)
    session.commit()

    return RedirectResponse(url="/ui/intereses", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/ui/intereses/{interes_id}/actualizar")
def ui_intereses_actualizar(
    interes_id: int,
    tasa: float = Form(...),
    tipo: str = Form(...),
    credito_id: int = Form(...),
    session: Session = Depends(get_session),
):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    credito = session.get(Credito, credito_id)
    if not credito:
        raise HTTPException(status_code=400, detail="Crédito no existe")

    interes.tasa = tasa
    interes.tipo = tipo
    interes.credito_id = credito_id

    session.commit()

    return RedirectResponse(url="/ui/intereses", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================
# RUTAS UI (HTML) - SIMULACIONES
# ============================================================

@app.get("/ui/simulaciones", response_class=HTMLResponse)
def ui_simulaciones(
    request: Request,
    session: Session = Depends(get_session),
):
    simulaciones = session.exec(select(Simulacion)).all()
    intereses = session.exec(select(Interes)).all()
    return templates.TemplateResponse(
        "simulaciones.html",
        {
            "request": request,
            "simulaciones": simulaciones,
            "intereses": intereses,
            "simulacion_editar": None,
            "form_action": "/ui/simulaciones/crear",
            "titulo_form": "Crear simulación",
        },
    )


@app.get("/ui/simulaciones/{simulacion_id}", response_class=HTMLResponse)
def ui_simulaciones_editar(
    simulacion_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    simulaciones = session.exec(select(Simulacion)).all()
    intereses = session.exec(select(Interes)).all()
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    return templates.TemplateResponse(
        "simulaciones.html",
        {
            "request": request,
            "simulaciones": simulaciones,
            "intereses": intereses,
            "simulacion_editar": simulacion,
            "form_action": f"/ui/simulaciones/{simulacion_id}/actualizar",
            "titulo_form": "Editar simulación",
        },
    )


@app.post("/ui/simulaciones/crear")
def ui_simulaciones_crear(
    interes_id: int = Form(...),
    cuotaMensual: float = Form(...),
    interesTotal: float = Form(...),
    saldoFinal: float = Form(...),
    session: Session = Depends(get_session),
):
    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=400, detail="Interés no existe")

    simulacion = Simulacion(
        interes_id=interes_id,
        cuotaMensual=cuotaMensual,
        interesTotal=interesTotal,
        saldoFinal=saldoFinal,
    )
    session.add(simulacion)
    session.commit()

    return RedirectResponse(url="/ui/simulaciones", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/ui/simulaciones/{simulacion_id}/actualizar")
def ui_simulaciones_actualizar(
    simulacion_id: int,
    interes_id: int = Form(...),
    cuotaMensual: float = Form(...),
    interesTotal: float = Form(...),
    saldoFinal: float = Form(...),
    session: Session = Depends(get_session),
):
    simulacion = session.get(Simulacion, simulacion_id)
    if not simulacion:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")

    interes = session.get(Interes, interes_id)
    if not interes:
        raise HTTPException(status_code=400, detail="Interés no existe")

    simulacion.interes_id = interes_id
    simulacion.cuotaMensual = cuotaMensual
    simulacion.interesTotal = interesTotal
    simulacion.saldoFinal = saldoFinal

    session.commit()

    return RedirectResponse(url="/ui/simulaciones", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================
# RUTAS UI (HTML) - REPORTES
# ============================================================

@app.get("/ui/reportes", response_class=HTMLResponse)
def ui_reportes(
    request: Request,
    session: Session = Depends(get_session),
):
    reportes = session.exec(select(Reporte)).all()
    usuarios = session.exec(select(Usuario)).all()
    creditos = session.exec(select(Credito)).all()
    simulaciones = session.exec(select(Simulacion)).all()

    return templates.TemplateResponse(
        "reportes.html",
        {
            "request": request,
            "reportes": reportes,
            "usuarios": usuarios,
            "creditos": creditos,
            "simulaciones": simulaciones,
            "reporte_editar": None,
            "form_action": "/ui/reportes/crear",
            "titulo_form": "Crear reporte",
        },
    )


@app.get("/ui/reportes/{reporte_id}", response_class=HTMLResponse)
def ui_reportes_editar(
    reporte_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    reportes = session.exec(select(Reporte)).all()
    usuarios = session.exec(select(Usuario)).all()
    creditos = session.exec(select(Credito)).all()
    simulaciones = session.exec(select(Simulacion)).all()
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    return templates.TemplateResponse(
        "reportes.html",
        {
            "request": request,
            "reportes": reportes,
            "usuarios": usuarios,
            "creditos": creditos,
            "simulaciones": simulaciones,
            "reporte_editar": reporte,
            "form_action": f"/ui/reportes/{reporte_id}/actualizar",
            "titulo_form": "Editar reporte",
        },
    )


@app.post("/ui/reportes/crear")
def ui_reportes_crear(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    usuario_id: int = Form(...),
    credito_id: int = Form(...),
    simulacion_id: int = Form(...),
    session: Session = Depends(get_session),
):
    reporte = Reporte(
        titulo=titulo,
        descripcion=descripcion,
        usuario_id=usuario_id,
        credito_id=credito_id,
        simulacion_id=simulacion_id,
    )
    session.add(reporte)
    session.commit()

    return RedirectResponse(url="/ui/reportes", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/ui/reportes/{reporte_id}/actualizar")
def ui_reportes_actualizar(
    reporte_id: int,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    usuario_id: int = Form(...),
    credito_id: int = Form(...),
    simulacion_id: int = Form(...),
    session: Session = Depends(get_session),
):
    reporte = session.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    reporte.titulo = titulo
    reporte.descripcion = descripcion
    reporte.usuario_id = usuario_id
    reporte.credito_id = credito_id
    reporte.simulacion_id = simulacion_id

    session.commit()

    return RedirectResponse(url="/ui/reportes", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================
# RUTAS UI (HTML) - HISTORIAL (solo lectura)
# ============================================================

@app.get("/ui/historial", response_class=HTMLResponse)
def ui_historial(
    request: Request,
    session: Session = Depends(get_session),
):
    historial = session.exec(select(Historial).order_by(Historial.fecha.desc())).all()
    return templates.TemplateResponse(
        "historial.html",
        {
            "request": request,
            "historial": historial,
        },
    )


# ============================================================
# Inclusión de routers (API JSON)
# ============================================================
app.include_router(usuario_router.router)
app.include_router(credito_router.router)
app.include_router(interes_router.router)
app.include_router(categoria_router.router)
app.include_router(simulacion_router.router)
app.include_router(reporte_router.router)
app.include_router(historial_router.router)


# -----------------------------
# Punto de entrada opcional
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)