#!/usr/bin/python3

# Import custom functions
from app.functions import createUser, getUserInfo, getUserID, datetime_handler
from app.functions import getInjuryRates, getWeather, verifyUser, dump_datetime
from connect import connect

# Import database objects
from app.module_auth.model_users import Users
from app.module_auth.model_incidents import Incidents
from app.module_auth.model_audits import Audits
from app.module_auth.model_actions import Actions
from app.module_auth.model_incidents import Manhours

# Import SQL Alchemy functions/operations
from sqlalchemy import func, desc
from sqlalchemy.orm import sessionmaker

# Import Flask operations
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import make_response, flash, session, Blueprint

from flask_httpauth import HTTPBasicAuth

# Import oauth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# Import advanced python scheduler for scheduled weather api calls
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import required python libraries
import psycopg2
import random
import string
import httplib2
import json
import requests
import datetime

# Print python version for troubleshooting purposes; must be Pyton 3 or higher.
import sys
print(sys.version)

from app import db as DBSession

#Define the blueprint:
mod_dashboard = Blueprint('mod_dashboard', __name__, url_prefix='/dashboard/')

# Main Page/Dashbaord


@mod_dashboard.route('/dashboard/')
def dashboard():
    """Loads the dashboard page"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])

    # Generates initial weather information
    weather = getWeather()
    # Starts apscheduler in the background
    scheduler = BackgroundScheduler()
    scheduler.start()
    # Creats a job for apscheduler to update the weather information every hour
    scheduler.add_job(
        func=getWeather,
        trigger=(IntervalTrigger(hours=1)),
        id='weather')

    # Connect to the database
    con = connect()
    Base.metadata.bind = con
    # Creates a session
    DBSession = sessionmaker(bind=con)
    dbsession = DBSession()

    # Fetches most recent incidents and injury rates
    results = dbsession.query(func.to_char(Incidents.date_time,
                                           'FMMonth FMDD, YYYY'),
                              func.to_char(Incidents.date_time,
                                           'HH24:MI'),
                              Incidents.case_num,
                              Incidents.incident_cat,
                              Incidents.description). \
        filter(Incidents.injury == 't'). \
        order_by(desc(Incidents.case_num)).all()
    injury_rate, manhours = getInjuryRates()
    length = len(results)

    # Fetches Audit Health
    health = []
    audit_results = dbsession.query(Audits.type, Audits.ans_1, Audits.ans_2,
                                    Audits.ans_3).all()
    length = len(audit_results)

    # Set the totals as floats at 0
    audit_def = 0.0
    b_total = 0.0
    audit_b_def = 0.0
    a_total = 0.0
    audit_a_def = 0.0
    h_total = 0.0
    audit_h_def = 0.0
    for i in audit_results:
        for j in range(len(i)):
            if i[j] is True:
                audit_def = audit_def + 1.0
        if i[0] == 'Behavior':
            # adding 3 because there are 3 answers total per audit.
            b_total = b_total + 3
            for k in range(len(i)):
                if i[k] is True:
                    audit_b_def = audit_b_def + 1.0
        if i[0] == 'Area Organization':
            a_total = a_total + 3
            for k in range(len(i)):
                if i[k] is True:
                    audit_a_def = audit_a_def + 1.0
        if i[0] == 'HAZWASTE':
            h_total = h_total + 3
            for k in range(len(i)):
                if i[k] is True:
                    audit_h_def = audit_h_def + 1.0

    # Creates percentage
    audit_perc = int(float(audit_def/(length*3)*100))
    health.append(audit_perc)
    audit_a_perc = int(float(audit_a_def/a_total*100))
    health.append(audit_a_perc)
    audit_b_perc = int(float(audit_b_def/b_total*100))
    health.append(audit_b_perc)
    audit_h_perc = int(float(audit_h_def/h_total*100))
    health.append(audit_h_perc)

    # Fetches Upcoming Action Items
    actions = dbsession.query(Actions.id,
                              func.to_char(Actions.date_time,
                                           'FMMonth FMDD, YYYY'),
                              func.to_char(Actions.date_time,
                                           'HH24:MI'),
                              Actions.case_id,
                              Actions.audit_id,
                              Actions.finding,
                              Actions.corrective_action,
                              func.to_char(Actions.due_date,
                                           'FMMonth FMDD, YYYY'),
                              Actions.open_close). \
        filter_by(open_close='t').order_by(Actions.due_date)
    print(user_profile[1])
    return render_template('dashboard.html',
                           incidents=results,
                           health=health,
                           actions=actions,
                           weather=weather,
                           injury_rate=injury_rate,
                           user_profile=user_profile,
                           manhours=manhours)

# User Profile


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    """loads the user profile page"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        email = session['email']
        picture = request.form.get('picture')
        position = request.form.get('position')

        if picture != '' and picture is not None:
            session['picture'] = picture
        if position != '' and position is not None:
            data = dbsession.query(Users).filter_by(email=email).one()
            data.position = position
            dbsession.commit()

        return redirect(url_for('profile'))
    else:
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        email = session['email']

        data = dbsession.query(Users).filter_by(email=email).one()

        position = data.position

        user_profile = (session['username'], session['picture'],
                        session['email'], position)
        return render_template('profile.html', user=user_profile)

# Resources/Help


@app.route('/resources/')
@app.route('/help/')
def resources():
    """Produces a Help/Resources page"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])
    return render_template('resources.html', user_profile=user_profile)