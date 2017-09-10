import psycopg2
import datetime
import json
import httplib2
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Users, Incidents, Audits, Actions, Manhours
from sqlalchemy import create_engine
from connect import connect


def dump_datetime(value):
    """Deserialize datetime object into string for JSON processing"""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


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
    print("Weather API Updated")
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
