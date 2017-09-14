from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Users, Incidents, Audits, Actions, Manhours
from sqlalchemy import create_engine
from connect import connect

# Connect to the database
con = connect()
Base.metadata.bind = con
# Creates a session
DBSession = sessionmaker(bind=con)
dbsession = DBSession()

incidents = dbsession.query(Incidents). \
    filter_by(case_num=22).first()

print(incidents)