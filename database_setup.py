# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from connect import connect

Base = declarative_base()

class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	email = Column(String(80), nullable = False)
	picture = Column(String(200))
	position = Column(String(80))

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

class Manhours(Base):
	__tablename__ = 'manhours'
	id = Column(Integer, primary_key = True	)
	year = Column(Integer, nullable = False)
	week = Column(Integer, nullable = False)
	hours = Column(Float, nullable = False)


con = connect()
Base.metadata.create_all(con)