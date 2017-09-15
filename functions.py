import psycopg2
import datetime
import json
import httplib2
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Users, Incidents, Audits, Actions, Manhours
from sqlalchemy import create_engine
from connect import connect
from functools import wraps
from flask import flash, redirect, url_for
import logging

# create logger
logger = logging.getLogger('Functions')
logger.setLevel(logging.WARNING)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# Decorators

def login_required(session):
    def tags_decorator(func):
        @wraps(func) # this requires an import
        def wrapper(*args, **kwargs):
            logger.info('Checking if user in logged in.')
            if 'username' not in session:
                logger.info('User is not logged in.')
                return redirect('login')
            else:
                logger.info('User is logged in.')
                return func(*args, **kwargs)
        return wrapper
    return tags_decorator


def owner_required(table, session):
    def tags_decorator(func):
        @wraps(func) # this requires an import
        def wrapper(id):
            logger.info('Checking if user in logged in.')
            if 'username' not in session:
                logger.info('User is not logged in.')
                return redirect('login')
            else:
                user_profile = (session['username'], session['picture'])
                logger.info('Imported user info: ' + session['username'] + ', ' + session['picture'])
                # Connect to the database
                con = connect()
                Base.metadata.bind = con
                # Creates a session
                DBSession = sessionmaker(bind=con)
                dbsession = DBSession()
                logger.info('Connected to DB.')
                if table == 'incidents':
                    query = dbsession.query(Incidents).filter_by(case_num=id).first()
                    logger.info('Queried Incidents')
                if table == 'audits':
                    query = dbsession.query(Audits).filter_by(id=id).first()
                    logger.info('Queried Audits')
                if table == 'actions':
                    query = dbsession.query(Actions).filter_by(id=id).first()
                    logger.info('Queried Actions')
                
                creator = int(query.user_id)
                ses_user = int(session['user_id'])
                if creator != ses_user:
                    logger.info('User is not the author of the report.')
                    flash("Sorry, %s,"
                          " you are not authorized to edit this report." %
                          session['username'])
                    return redirect('/incidents/')
                else:
                    logger.info('User is the verified author of the report.')
                    return func(id)
        return wrapper
    return tags_decorator


def check_if_report_exists(table, session):
    def tags_decorator(func):
        @wraps(func) # this requires an import
        def wrapper(id):
            # Connect to the database
            con = connect()
            Base.metadata.bind = con
            # Creates a session
            DBSession = sessionmaker(bind=con)
            dbsession = DBSession()
            logger.info('Connected to DB.')
            if table == 'incidents':
                query = dbsession.query(Incidents).filter_by(case_num=id).first()
                logger.info('Queried Incidents')
            if table == 'audits':
                query = dbsession.query(Audits).filter_by(id=id).first()
                logger.info('Queried Audits')
            if table == 'actions':
                query = dbsession.query(Actions).filter_by(id=id).first()
                logger.info('Queried Actions')
            if query is None:
                logger.info('No report exists.')
                flash("Sorry, this report does not exists")
                return redirect('/dashboard/')
            else:
                logger.info('Report exists in the DB.')
                return func(id)
        return wrapper
    return tags_decorator

# Functions


def createUser(session):
    # Connect to the database
    con = connect()
    Base.metadata.bind = con
    # Creates a session
    DBSession = sessionmaker(bind=con)
    dbsession = DBSession()

    name = session['username']
    email = session['email']
    picture = session['picture']
    position = ''

    insert = Users(name=name,
                   email=email,
                   picture=picture,
                   position=position)
    dbsession.add(insert)
    dbsession.commit()

    query = dbsession.query(Users).filter_by(name=name).one()
    new_id = query.id
    return new_id


def verifyUser(email, password):
    # Connect to the database
    con = connect()
    Base.metadata.bind = con
    # Creates a session
    DBSession = sessionmaker(bind=con)
    dbsession = DBSession()
    user = dbsession.query(Users).filter_by(email=email).first()
    verify = user.verify_password(password)
    if not user or not user.verify_password(password):
        return False
    else:
        return True


def getUserInfo(id):
    # Connect to the database
    con = connect()
    Base.metadata.bind = con
    # Creates a session
    DBSession = sessionmaker(bind=con)
    dbsession = DBSession()

    query = dbsession.query(Users).filter_by(id=id).all()

    return query


def getUserID(email):
    # Connect to the database
    con = connect()
    Base.metadata.bind = con
    # Creates a session
    DBSession = sessionmaker(bind=con)
    dbsession = DBSession()

    query = dbsession.query(Users).filter_by(email=email).first()

    if query is None:
        user = None
    else:
        user = str(query.id)
    return user


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


def getWeather():
    # http://api.openweathermap.org/data/2.5/forecast?id=4508722&APPID=00b1eab8137a0b1d81025d667dbb2f17
    # app_id = 00b1eab8137a0b1d81025d667dbb2f17
    # City ID for Cincinnati, OH
    # city_id = 4508722
    url = "http://api.openweathermap.org/data/2.5/forecast?id=4508722&APPID=" \
        "00b1eab8137a0b1d81025d667dbb2f17&units=imperial"
    h = httplib2.Http()

    raw = h.request(url, 'GET')[1]

    results = json.loads(raw.decode())

    weather_main = results['list'][0]['weather'][0]['main']
    weather_desc = results['list'][0]['weather'][0]['description']
    weather_temp = results['list'][0]['main']['temp']
    weather_icon = results['list'][0]['weather'][0]['icon']

    weather_data = (weather_main, weather_desc, weather_temp, weather_icon)
    logger.info('Weather Data Updated')
    return weather_data


def getInjuryRates():
    # Connect to the database
    con = connect()
    Base.metadata.bind = con
    # Creates a session
    DBSession = sessionmaker(bind=con)
    dbsession = DBSession()

    query_fa = dbsession. \
        query(func.count(Incidents.incident_type)). \
        filter_by(incident_type='FA')
    query_ri = dbsession. \
        query(func.count(Incidents.incident_type)). \
        filter_by(incident_type='RI')
    query_rd = dbsession. \
        query(func.count(Incidents.incident_type)). \
        filter_by(incident_type='RD')
    query_lti = dbsession. \
        query(func.count(Incidents.incident_type)). \
        filter_by(incident_type='LTI')

    total_fa = query_fa[0][0]
    total_ri = query_ri[0][0]
    total_rd = query_rd[0][0]
    total_lti = query_lti[0][0]

    total_rir = total_ri+total_rd+total_lti
    total_tir = total_ri+total_rd+total_lti+total_fa

    hours_query = dbsession.query(func.sum(Manhours.hours)). \
        filter_by(year=2017)
    manhours = hours_query[0][0]

    fair = round(float(total_fa*200000)/float(manhours), 2)
    rir = round(float(total_rir*200000)/float(manhours), 2)
    lti = round(float(total_lti*200000)/float(manhours), 2)
    ori = round(float(total_ri*200000)/float(manhours), 2)
    tir = round(float(total_tir*200000)/float(manhours), 2)

    injury_rate = (fair, rir, lti, ori, tir)

    return injury_rate, manhours
