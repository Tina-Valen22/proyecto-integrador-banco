from sqlmodel import SQLModel, create_engine, Session
import os

# --- CONFIGURAR BASE DE DATOS PARA RENDER O LOCAL ---

# Si Render define DATABASE_URL, úsala. Si no, usa SQLite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./banco.db")

# Cuando es SQLite en Render, debe usar connect_args especiales.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)


# --- CREAR TABLAS ---
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# --- SESIONES ---
def get_session():
    with Session(engine) as session:
        yield session
