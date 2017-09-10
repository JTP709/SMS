# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import DateTime, Boolean, Enum, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from connect import connect

Base = declarative_base()

class Incidents(Base):
    __tablename__ = 'incidents'
    case_num = Column(Integer, primary_key=True)
    date_time = Column(DateTime)
    incident_type = Column('incident_type',
                           Enum('FA',
                                'RI',
                                'RD',
                                'LTI',
                                'PIT Incident',
                                'Near Miss',
                                'HAZMAT',
                                name='type'))
    incident_cat = Column('incident_cat',
                          Enum('Unsafe Act',
                               'Unsafe Behavior',
                               'Unsafe Condition',
                               name='category'))
    injury = Column(Boolean, nullable=False)
    property_damage = Column(Boolean, nullable=False)
    description = Column(String, nullable=False)
    root_cause = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
               'case_number': self.case_num,
               'date_time': dump_datetime(self.date_time),
               'incident_type': self.incident_type,
               'incident_cat': self.incident_cat,
               'injury_case': self.injury,
               'property_damage_case': self.property_damage,
               'description': self.description,
               'root_cause': self.root_cause,
               'user_id': self.user_id,
               }
               