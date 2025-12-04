from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

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
# Templates y archivos estáticos
# -----------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
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
    # Tu pantalla de inicio está en home.html (que extiende base.html)
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/health")
def health_check():
    """
    Endpoint simple de salud para verificar que la API está arriba.
    """
    return {"status": "ok", "message": "API Integrador Banco funcionando"}


# -----------------------------
# RUTAS UI (HTML) - Vistas
# -----------------------------

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
        },
    )


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
        },
    )


@app.get("/ui/categorias", response_class=HTMLResponse)
def ui_categorias(
    request: Request,
    session: Session = Depends(get_session),
):
    categorias = session.exec(select(Categoria)).all()
    creditos = session.exec(select(Credito)).all()
    relaciones = session.exec(select(CreditoCategoria)).all()

    # Mapeo categoria_id -> primer credito_id asociado (para mostrar/prellenar)
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
        },
    )


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
        },
    )


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
        },
    )


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
        },
    )


@app.get("/ui/historial", response_class=HTMLResponse)
def ui_historial(
    request: Request,
    session: Session = Depends(get_session),
):
    historial = session.exec(select(Historial)).all()
    return templates.TemplateResponse(
        "historial.html",
        {
            "request": request,
            "historial": historial,
        },
    )


# -----------------------------
# Inclusión de routers (API JSON)
# -----------------------------
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