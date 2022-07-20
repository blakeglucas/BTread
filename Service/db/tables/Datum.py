from sqlalchemy import Table, Column, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from ..tables.Session import SessionTable

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

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

class DatumTableSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DatumTable
        include_fk = True
        load_instance = True