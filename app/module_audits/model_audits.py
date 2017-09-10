# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import DateTime, Boolean, Enum, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from connect import connect

Base = declarative_base()

class Audits(Base):
    __tablename__ = 'audits'
    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime)
    type = Column('type',
                  Enum('Behavior',
                       'Area Organization',
                       'HAZWASTE',
                       name='audit_type'))
    que_1 = Column(String, nullable=False)
    que_2 = Column(String, nullable=False)
    que_3 = Column(String, nullable=False)
    ans_1 = Column(Boolean, nullable=False)
    ans_2 = Column(Boolean, nullable=False)
    ans_3 = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
               'id': self.id,
               'date_time': dump_datetime(self.date_time),
               'type': self.type,
               'que_1': self.que_1,
               'que_2': self.que_2,
               'que_3': self.que_3,
               'ans_1': self.ans_1,
               'ans_2': self.ans_2,
               'ans_3': self.ans_3,
               'user_id': self.user_id
               }
