# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Enum, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

def connect(user='safety', password='safety',db='safety_v2', host='localhost', port=5432):
    """Returns a connection and a metadata object"""
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password,host, port, db)
    con = create_engine(url, client_encoding ='utf8')
    return con

def dump_datetime(value):
    """Deserialize datetime object into string for JSON processing"""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)
    picture = Column(String(200))
    position = Column(String(80))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
        'id':self.id,
        'name':self.name,
        'email':self.email,
        'picture_url':self.picture,
        'job_title':self.position
        }

class Incidents(Base):
    __tablename__ = 'incidents'
    case_num = Column(Integer, primary_key = True)
    date_time = Column(DateTime)
    incident_type = Column('incident_type', Enum('FA','RI','RD','LTI','PIT Incident','Near Miss', 'HAZMAT', name = 'type'))
    incident_cat = Column('incident_cat', Enum('Unsafe Act','Unsafe Behavior','Unsafe Condition', name = 'category'))
    injury = Column(Boolean, nullable = False)
    property_damage = Column(Boolean, nullable = False)
    description = Column(String, nullable = False)
    root_cause = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
        'case_number':self.case_num,
        'date_time':dump_datetime(self.date_time),
        'incident_type':self.incident_type,
        'incident_cat':self.incident_cat,
        'injury_case':self.injury,
        'property_damage_case':self.property_damage,
        'description':self.description,
        'root_cause':self.root_cause,
        'user_id':self.user_id,
        }

class Audits(Base):
    __tablename__ = 'audits'
    id = Column(Integer, primary_key = True)
    date_time = Column(DateTime)
    type = Column('type', Enum('Behavior', 'Area Organization','HAZWASTE', name = 'audit_type'))
    que_1 = Column(String, nullable = False)
    que_2 = Column(String, nullable = False)
    que_3 = Column(String, nullable = False)
    ans_1 = Column(Boolean, nullable = False)
    ans_2 = Column(Boolean, nullable = False)
    ans_3 = Column(Boolean, nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
        'id':self.id,
        'date_time':dump_datetime(self.date_time),
        'type':self.type,
        'que_1':self.que_1,
        'que_2':self.que_2,
        'que_3':self.que_3,
        'ans_1':self.ans_1,
        'ans_2':self.ans_2,
        'ans_3':self.ans_3,
        'user_id':self.user_id
        }

class Actions(Base):
    __tablename__ = 'action_items'
    id = Column(Integer, primary_key = True)
    date_time = Column(DateTime)
    case_id = Column(Integer, ForeignKey('incidents.case_num'))
    audit_id = Column(Integer, ForeignKey('audits.id'))
    finding = Column(String)
    corrective_action = Column(String)
    due_date = Column(DateTime)
    open_close = Column(Boolean, nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'))
    incident = relationship(Incidents)
    audit = relationship(Audits)
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
        'id':self.id,
        'date_time':dump_datetime(self.date_time),
        'case_id':self.case_id,
        'audit_id':self.audit_id,
        'finding':self.finding,
        'corrective_action':self.corrective_action,
        'due_date':dump_datetime(self.due_date),
        'open_close':self.open_close,
        'user_id':self.user_id,
        }

class Manhours(Base):
    __tablename__ = 'manhours'
    id = Column(Integer, primary_key = True )
    year = Column(Integer, nullable = False)
    week = Column(Integer, nullable = False)
    hours = Column(Float, nullable = False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
        'id':self.id,
        'year':self.year,
        'week':self.week,
        'hours':self.hours
        }

con = connect()
Base.metadata.create_all(con)