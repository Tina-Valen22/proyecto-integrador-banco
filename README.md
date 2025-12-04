# Proyecto Integrador – Banco Digital

Este proyecto implementa un sistema bancario utilizando **FastAPI**, **SQLAlchemy**, **Pydantic** y una arquitectura modular. Permite gestionar usuarios, créditos, categorías, tasas de interés, simulaciones financieras y reportes.

---

## 🚀 Tecnologías principales

- **FastAPI**
- **Python 3**
- **SQLAlchemy**
- **SQLite**
- **Pydantic**
- **Routers modulares**
- **(Opcional) Jinja2 para interfaz HTML**

---

## 📁 Estructura del Proyecto

proyecto-integrador-banco/
│
├── main.py
├── database.py
├── models/
│ ├── usuario.py
│ ├── credito.py
│ ├── categoria.py
│ ├── interes.py
│ ├── historial.py
│ ├── reporte.py
│ └── simulacion.py
│
├── routers/
│ ├── usuario_router.py
│ ├── credito_router.py
│ ├── categoria_router.py
│ ├── interes_router.py
│ ├── historial_router.py
│ ├── reporte_router.py
│ └── simulacion_router.py
│
├── templates/
│ ├── credito.html
│ ├── categoria.html
│ ├── interes.html
│ ├── historial.html
│ ├── reporte.html
│ └── simulacion.html
│ └── usuario.html
└── static/
  └── styles.css
