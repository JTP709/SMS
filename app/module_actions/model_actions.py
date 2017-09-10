# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import DateTime, Boolean, Enum, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from connect import connect

Base = declarative_base()

class Actions(Base):
    __tablename__ = 'action_items'
    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime)
    case_id = Column(Integer, ForeignKey('incidents.case_num'))
    audit_id = Column(Integer, ForeignKey('audits.id'))
    finding = Column(String)
    corrective_action = Column(String)
    due_date = Column(DateTime)
    open_close = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    incident = relationship(Incidents)
    audit = relationship(Audits)
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
               'id': self.id,
               'date_time': dump_datetime(self.date_time),
               'case_id': self.case_id,
               'audit_id': self.audit_id,
               'finding': self.finding,
               'corrective_action': self.corrective_action,
               'due_date': dump_datetime(self.due_date),
               'open_close': self.open_close,
               'user_id': self.user_id,
               }
