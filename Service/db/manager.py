import atexit
from config import DB_FILE
from datetime import datetime
import os
from sqlalchemy import create_engine, event, insert
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.orm import Session, declarative_base
from .tables.Datum import DatumTable
from .tables.Session import SessionTable
from .tables.Base import Base

engine = create_engine(f'sqlite:///{os.path.abspath(DB_FILE)}', future=True)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

conn: Connection = engine.connect()

session = Session(engine)
atexit.register(session.close)

Base.metadata.create_all(engine)

def start_session():
    s = SessionTable(StartTime=datetime.utcnow())
    session.add(s)
    session.commit()
    session.flush()
    return s

def finish_session(session_id: int):
    existing_session: SessionTable = session.get(SessionTable, session_id)
    if existing_session:
        final_datum: DatumTable = session.query(DatumTable).order_by(DatumTable.Timestamp.desc()).first()
        if not final_datum:
            print('No session endpoint, ignoring')
            return None
        existing_session.EndTime = datetime.utcnow()
        existing_session.Calories = final_datum.Calories
        existing_session.Distance = final_datum.Distance
        session.add(existing_session)
        session.commit()
        session.flush()
        return existing_session
    else:
        print(f'No existing session with ID "{session_id}')
        return None


def new_datum(speed: float, elapsed_time: int, calories: int, distance: int, session_id: int):
    d = DatumTable(
        Timestamp=datetime.utcnow(),
        Speed=speed,
        ElapsedTime=elapsed_time,
        Calories=calories,
        Distance=distance,
        SessionID=session_id
    )
    session.add(d)
    session.commit()
    session.flush()
    return d