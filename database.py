# database.py
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
        if not session.exec(select(Usuario)).first():
            # crear usuarios
            u1 = Usuario(nombre="Juan Pérez", ingresos=3000000, gastos=1200000)
            u2 = Usuario(nombre="María López", ingresos=4500000, gastos=1800000)
            session.add_all([u1, u2])
            session.commit()
            session.refresh(u1)
            session.refresh(u2)

            # crear creditos vinculados a los usuarios ya persistidos
            c1 = Credito(monto=10000000, plazo=12, tipo="Personal", usuario_id=u1.idUsuario)
            c2 = Credito(monto=25000000, plazo=240, tipo="Hipotecario", usuario_id=u2.idUsuario)
            session.add_all([c1, c2])
            session.commit()
            session.refresh(c1)
            session.refresh(c2)

            # intereses
            i1 = Interes(tasa=0.05, tipo="Fijo", credito_id=c1.idCredito)
            i2 = Interes(tasa=0.035, tipo="Variable", credito_id=c2.idCredito)
            session.add_all([i1, i2])
            session.commit()
            session.refresh(i1)
            session.refresh(i2)

            # simulaciones
            s1 = Simulacion(cuotaMensual=900000, interesTotal=80000, saldoFinal=10800000, interes_id=i1.idInteres)
            s2 = Simulacion(cuotaMensual=1100000, interesTotal=140000, saldoFinal=26400000, interes_id=i2.idInteres)
            session.add_all([s1, s2])
            session.commit()
            session.refresh(s1)
            session.refresh(s2)

            # reportes
            r1 = Reporte(grafico="grafico1.png", estadisticas="Estadísticas de Juan", simulacion_id=s1.idSimulacion)
            r2 = Reporte(grafico="grafico2.png", estadisticas="Estadísticas de María", simulacion_id=s2.idSimulacion)
            session.add_all([r1, r2])
            session.commit()
            print("✅ Datos iniciales creados correctamente.")
