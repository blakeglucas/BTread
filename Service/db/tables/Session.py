from sqlalchemy import Table, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, relationship

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from .Base import Base
from .Datum import DatumTableSchema

class SessionTable(Base):
    __tablename__ = 'Session'
    SessionID = Column('SessionID', Integer, primary_key=True)
    StartTime = Column('StartTime', DateTime)
    EndTime = Column('EndTime', DateTime, nullable=True)
    Distance = Column('Distance', Integer, nullable=True)
    Calories = Column('Calories', Integer, nullable=True)
    Data = relationship('DatumTable')

class SessionTableSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SessionTable
        include_relationships = True
        load_instance = True
    Data = Nested(DatumTableSchema, many=True)