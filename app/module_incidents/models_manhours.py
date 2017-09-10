# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import DateTime, Boolean, Enum, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from connect import connect

class Manhours(Base):
    __tablename__ = 'manhours'
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    hours = Column(Float, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
               'id': self.id,
               'year': self.year,
               'week': self.week,
               'hours': self.hours
               }
