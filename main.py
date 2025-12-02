from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import create_db_and_tables
from routers import (
    usuario_router,
    credito_router,
    categoria_router,
    historial_router,
    interes_router,
    simulacion_router,
    reporte_router
)

app = FastAPI(title="Simulador Créditos Bancarios")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    create_db_and_tables()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Routers
app.include_router(usuario_router.router)
app.include_router(credito_router.router)
app.include_router(categoria_router.router)
app.include_router(historial_router.router)
app.include_router(interes_router.router)
app.include_router(simulacion_router.router)
app.include_router(reporte_router.router)
