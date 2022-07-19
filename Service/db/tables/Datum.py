from sqlalchemy import Table, Column, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from ..tables.Session import SessionTable

from .Base import Base

class DatumTable(Base):
    __tablename__ = 'Datum'
    DatumID = Column('DatumID', Integer, primary_key=True)
    Timestamp = Column('Timestamp', DateTime)
    Speed = Column('Speed', Float)
    ElapsedTime = Column('ElapsedTime', Integer)
    Calories = Column('Calories', Integer)
    Distance = Column('Distance', Integer)
    SessionID = Column('SessionID', Integer, ForeignKey(SessionTable.SessionID), nullable=False)