from sqlalchemy import Table, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base

from .Base import Base

class SessionTable(Base):
    __tablename__ = 'Session'
    SessionID = Column('SessionID', Integer, primary_key=True)
    StartTime = Column('StartTime', DateTime)
    EndTime = Column('EndTime', DateTime, nullable=True)
    Distance = Column('Distance', Integer, nullable=True)
    Calories = Column('Calories', Integer, nullable=True)