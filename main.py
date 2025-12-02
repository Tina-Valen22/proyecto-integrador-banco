from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from database import create_db_and_tables
from routers.usuario_router import router as usuario_router
from routers.credito_router import router as credito_router
from routers.interes_router import router as interes_router
from routers.historial_router import router as historial_router
from routers.categoria_router import router as categoria_router
from routers.reporte_router import router as reporte_router
from routers.simulacion_router import router as simulacion_router

app = FastAPI(title="Proyecto Banco")

# ----- TEMPLATES Y ARCHIVOS ESTÁTICOS -----
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ----- REGISTRO DE ROUTERS -----
app.include_router(usuario_router)
app.include_router(credito_router)
app.include_router(interes_router)
app.include_router(historial_router)
app.include_router(categoria_router)
app.include_router(reporte_router)
app.include_router(simulacion_router)

@app.on_event("startup")
def startup():
    create_db_and_tables()
