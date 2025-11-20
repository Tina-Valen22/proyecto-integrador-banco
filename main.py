from fastapi import FastAPI
from database import crear_bd_y_tablas
from routers import (
    usuario_router,
    credito_router,
    interes_router,
    simulacion_router,
    reporte_router,
    historial_router
)

app = FastAPI(title="Simulador de Créditos Bancarios")

@app.on_event("startup")
def iniciar_bd():
    crear_bd_y_tablas()

# Registrar routers
app.include_router(usuario_router.router)
app.include_router(credito_router.router)
app.include_router(interes_router.router)
app.include_router(simulacion_router.router)
app.include_router(reporte_router.router)
app.include_router(historial_router.router)
