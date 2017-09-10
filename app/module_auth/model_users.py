# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import DateTime, Boolean, Enum, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from connect import connect

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(200))
    position = Column(String(80))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
               'id': self.id,
               'name': self.name,
               'email': self.email,
               'picture_url': self.picture,
               'job_title': self.position
               }
               