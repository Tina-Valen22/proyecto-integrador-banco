from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import create_db_and_tables

# Routers
from routers import (
    usuario_router,
    credito_router,
    interes_router,
    categoria_router,
    simulacion_router,
    reporte_router,
    historial_router,
)

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
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health_check():
    """
    Endpoint simple de salud para verificar que la API está arriba.
    """
    return {"status": "ok", "message": "API Integrador Banco funcionando"}


# -----------------------------
# Inclusión de routers
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
# Esto es útil si quieres ejecutar: python main.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)