# database.py
from datetime import datetime
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine, select

from models.usuario import Usuario
from models.credito import Credito
from models.historial import Historial
from models.interes import Interes
from models.simulacion import Simulacion
from models.reporte import Reporte

# -------------------------
# Configuración del engine
# -------------------------
sqlite_file_name = "banco.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# echo=True muestra el SQL en consola, útil mientras depuras
engine = create_engine(sqlite_url, echo=False)


# -------------------------
# Creación de BD y tablas
# -------------------------
def create_db_and_tables() -> None:
    """
    Crea todas las tablas definidas en los modelos (SQLModel.metadata)
    y carga datos iniciales si la BD está vacía.
    """
    SQLModel.metadata.create_all(engine)
    create_initial_data()


# -------------------------
# Datos iniciales de ejemplo
# -------------------------
def create_initial_data() -> None:
    """
    Carga algunos registros de ejemplo sólo si no hay usuarios en la BD.
    Así no duplica datos cada vez que se reinicia la app.
    """
    with Session(engine) as session:
        # ¿Ya hay datos? Si hay al menos un usuario, no hacemos nada.
        existing_user = session.exec(select(Usuario)).first()
        if existing_user:
            return

        # -----------------------------
        # Usuarios de ejemplo
        # -----------------------------
        u1 = Usuario(
            nombre="Juan Pérez",
            ingresos=3_000_000,
            gastos=1_200_000,
            correo="juan.perez@example.com",
            telefono="3001234567",
        )
        u2 = Usuario(
            nombre="María López",
            ingresos=4_500_000,
            gastos=1_800_000,
            correo="maria.lopez@example.com",
            telefono="3109876543",
        )

        session.add(u1)
        session.add(u2)
        session.commit()
        session.refresh(u1)
        session.refresh(u2)

        # -----------------------------
        # Créditos de ejemplo
        # -----------------------------
        c1 = Credito(
            monto=10_000_000,
            plazo=12,
            tipo="Personal",
            descripcion="Crédito personal de libre inversión",
            usuario_id=u1.idUsuario,
        )
        c2 = Credito(
            monto=20_000_000,
            plazo=24,
            tipo="Vehículo",
            descripcion="Crédito para compra de vehículo",
            usuario_id=u2.idUsuario,
        )

        session.add(c1)
        session.add(c2)
        session.commit()
        session.refresh(c1)
        session.refresh(c2)

        # -----------------------------
        # Interés de ejemplo
        # -----------------------------
        i1 = Interes(
            tasa=1.5,
            tipo="Fijo",
            credito_id=c2.idCredito,  # por ejemplo, asociado al crédito de vehículo
        )
        session.add(i1)
        session.commit()
        session.refresh(i1)

        # -----------------------------
        # Simulación de ejemplo
        # -----------------------------
        s1 = Simulacion(
            cuotaMensual=950_000.0,
            interesTotal=2_800_000.0,
            saldoFinal=22_800_000.0,
            interes_id=i1.idInteres,
        )
        session.add(s1)
        session.commit()
        session.refresh(s1)

        # -----------------------------
        # Reporte de ejemplo
        # IMPORTANTE: fecha NUNCA en NULL
        # -----------------------------
        r1 = Reporte(
            titulo="Reporte 1",
            descripcion="Compra general (vehiculo)",
            fecha=datetime.now(),  # <- aquí está el cambio clave
            usuario_id=u2.idUsuario,
            credito_id=c2.idCredito,
            simulacion_id=s1.idSimulacion,
        )
        session.add(r1)

        # -----------------------------
        # Historial de inicialización
        # -----------------------------
        h = Historial(
            entidad="Sistema",
            accion="INICIALIZACIÓN",
            descripcion="Base de datos creada y datos de ejemplo cargados",
            fecha=datetime.now(),
        )
        session.add(h)

        session.commit()


# -------------------------
# Dependencia para FastAPI
# -------------------------
def get_session() -> Iterator[Session]:
    """
    Dependencia para FastAPI.
    Uso:
        def endpoint(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session