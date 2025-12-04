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

✨ Principales Funcionalidades
✔ Gestión de Usuarios

Crear usuarios

Editar / listar

Ver detalles

Subir archivo de cédula

Guardar información económica

✔ Gestión de Créditos

CRUD completo

Relación con usuarios, categorías e intereses

✔ Categorías

Crear categorías

Asignarlas a créditos

✔ Tasas de Interés

CRUD

Uso en simulaciones

✔ Simulaciones de Crédito

Cálculo de cuota

Interés total

Saldo final

✔ Historial de Movimientos

Registro de eventos del crédito

✔ Reportes

Generación de reportes basados en usuario, crédito y simulación

🧩 Diagramas (prontos para generar)

Los siguientes diagramas pueden generarse como imágenes:

📌 Diagrama UML de Clases

Incluye:

Usuario

Crédito

Categoría

Interés

Simulación

Reporte

Historial

📌 Diagrama de Endpoints

Muestra todas las rutas FastAPI agrupadas por módulo.

🔧 Instalación

1️⃣ Clona el repositorio

git clone <URL_DEL_REPOSITORIO>
cd proyecto-integrador-banco


2️⃣ Instala dependencias

pip install -r requirements.txt

▶ Ejecutar el Servidor
uvicorn main:app --reload


Servidor disponible en:
➡ http://127.0.0.1:8000/

📚 Documentación Automática

FastAPI incluye 2 documentaciones automáticas:

Swagger UI: /docs

ReDoc: /redoc

🗂 Resumen del Modelo de Datos

Usuario
Tiene uno o varios créditos.

Crédito
Está asociado a un usuario, categoría e interés.

Simulación
Calcula la cuota y totales del crédito.

Historial
Guarda eventos importantes.

Reporte
Junta usuario + crédito + simulación.

👤 Objetivo del Proyecto

Construir un sistema web bancario que permita realizar:

Registro de usuarios

Gestión de créditos

Cálculo de simulaciones

Control de historial y reportes

Administración vía API y vistas web

Es ideal para demostrar:
✔ Modelado de base de datos
✔ Uso de FastAPI
✔ Arquitectura modular
✔ Integración de vistas HTML
✔ CRUD completos
