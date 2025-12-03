from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from routers.usuario_router import router as usuario_router
from routers.credito_router import router as credito_router
from routers.categoria_router import router as categoria_router
from routers.interes_router import router as interes_router
from routers.simulacion_router import router as simulacion_router
from routers.reporte_router import router as reporte_router
from routers.historial_router import router as historial_router

from database import create_db_and_tables


app = FastAPI(title="Banco - Sistema de Simulación")

# Templates
templates = Jinja2Templates(directory="templates")

# Static
app.mount("/static", StaticFiles(directory="static"), name="static")


# Crear BD al iniciar
@app.on_event("startup")
def startup_event():
    create_db_and_tables()


# Página principal (home)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# Routers
app.include_router(usuario_router)
app.include_router(credito_router)
app.include_router(categoria_router)
app.include_router(interes_router)
app.include_router(simulacion_router)
app.include_router(reporte_router)
app.include_router(historial_router)
