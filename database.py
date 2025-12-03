from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # NECESARIO PARA RENDER
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
