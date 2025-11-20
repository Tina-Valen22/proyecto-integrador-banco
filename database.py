from sqlmodel import SQLModel, create_engine, Session
from models.usuario import Usuario
from models.credito import Credito
from models.interes import Interes
from models.simulacion import Simulacion
from models.reporte import Reporte
from models.historial import Historial

DATABASE_URL = "sqlite:///./banco.db"
engine = create_engine(DATABASE_URL, echo=True)

def crear_bd_y_tablas():
    SQLModel.metadata.create_all(engine)
    crear_datos_iniciales()

def crear_datos_iniciales():
    with Session(engine) as session:
        if not session.query(Usuario).first():  # Solo si está vacía
            u1 = Usuario(nombre="Juan Pérez", ingresos=3000, gastos=1200)
            u2 = Usuario(nombre="María López", ingresos=4500, gastos=1800)

            session.add_all([u1, u2])
            session.commit()

            c1 = Credito(monto=10000, plazo=12, tipo="Personal", usuario_id=u1.idUsuario)
            c2 = Credito(monto=25000, plazo=24, tipo="Hipotecario", usuario_id=u2.idUsuario)

            session.add_all([c1, c2])
            session.commit()

            i1 = Interes(tasa=0.05, tipo="Fijo", credito_id=c1.idCredito)
            i2 = Interes(tasa=0.03, tipo="Variable", credito_id=c2.idCredito)

            session.add_all([i1, i2])
            session.commit()

            s1 = Simulacion(cuotaMensual=900, interesTotal=800, saldoFinal=10800, interes_id=i1.idInteres)
            s2 = Simulacion(cuotaMensual=1100, interesTotal=1400, saldoFinal=26400, interes_id=i2.idInteres)

            session.add_all([s1, s2])
            session.commit()

            r1 = Reporte(grafico="grafico1.png", estadisticas="Estadísticas de Juan", simulacion_id=s1.idSimulacion)
            r2 = Reporte(grafico="grafico2.png", estadisticas="Estadísticas de María", simulacion_id=s2.idSimulacion)

            session.add_all([r1, r2])
            session.commit()

            print("✅ Datos iniciales creados correctamente.")
