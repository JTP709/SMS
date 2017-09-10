#!/usr/bin/python3

# Import custom functions
from functions import createUser, getUserInfo, getUserID, datetime_handler
from functions import getInjuryRates, getWeather, verifyUser
from connect import connect
# Import database objects
from database_setup import Base, Users, Incidents, Audits, Actions
from database_setup import Manhours
# Import SQL Alchemy functions/operations
from sqlalchemy import func, desc
from sqlalchemy.orm import sessionmaker
# Import Flask operations
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import make_response, flash, session
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

# Incident Manager


@app.route('/incidents/')
def incidents():
    """Loads the incidents page"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

    results = dbsession.query(Incidents.case_num,
                              func.to_char(Incidents.date_time,
                                           'FMMonth FMDD, YYYY'),
                              func.to_char(Incidents.date_time,
                                           'HH24:MI'),
                              Incidents.incident_type,
                              Incidents.incident_cat,
                              Incidents.injury,
                              Incidents.property_damage,
                              Incidents.description,
                              Incidents.root_cause). \
        order_by(desc(Incidents.case_num)).all()
    length = len(results)
    # Get the injury rates
    injury_rate, manhours = getInjuryRates()

    return render_template('incidents.html',
                           incidents=results,
                           length=length,
                           injury_rate=injury_rate,
                           user_profile=user_profile,
                           manhours=manhours)
    db.close()


@app.route('/incidents/new/', methods=['GET', 'POST'])
def newIncident():
    """Loads the page to submit a new incident report"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()
        user_id = getUserID(session['email'])
        incidents = Incidents(date_time=request.form['date_time'],
                              incident_type=request.form['incident_type'],
                              incident_cat=request.form['incident_cat'],
                              injury=request.form['injury'],
                              property_damage=request.form['property_damage'],
                              description=request.form['description'],
                              root_cause=request.form['root_cause'],
                              user_id=user_id)
        dbsession.add(incidents)
        dbsession.commit()
        getcase_id = dbsession.query(Incidents.case_num). \
            order_by(desc(Incidents.case_num)).first()
        case_id = getcase_id[0]
        ca = request.form['corrective_action']
        action_items = Actions(finding=request.form['description'],
                               corrective_action=ca,
                               due_date=request.form['due_date'],
                               open_close='t',
                               user_id=user_id,
                               case_id=case_id)

        dbsession.add(action_items)
        dbsession.commit()

        return redirect(url_for('incidents'))
    else:
        user_profile = (session['username'], session['picture'])
        return render_template('incidents_new.html',
                               user_profile=user_profile)


@app.route('/incidents/edit/<int:id>/', methods=['GET', 'POST'])
def editIncident(id):
    """Page to edit an existing incident report"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        date_time = request.form.get('date_time')
        incident_type = request.form.get('incident_type')
        incident_cat = request.form.get('incident_cat')
        injury = request.form.get('injury')
        property_damage = request.form.get('property_damage')
        description = request.form.get('description')
        root_cause = request.form.get('root_cause')

        data = dbsession.query(Incidents).filter_by(case_num=id).one()

        # Creates a seperate insert execution per input generated.

        if date_time != '' and date_time is not None:
            data.date_time = date_time
            dbsession.commit()
        if incident_type != '' and incident_type is not None:
            data.incident_type = incident_type
            dbsession.commit()
        if incident_cat != '' and incident_cat is not None:
            data.incident_cat = incident_cat
            dbsession.commit()
        if injury != '' and injury is not None:
            data.injury = injury
            dbsession.commit()
        if property_damage != '' and property_damage is not None:
            data.property_damage = property_damage
            dbsession.commit()
        if description != '' and description is not None:
            data.description = description
            dbsession.commit()
        if root_cause != '' and root_cause is not None:
            data.root_cause = root_cause
            dbsession.commit()

        finding = request.form.get('description')
        corrective_action = request.form.get('corrective_action')
        due_date = request.form.get('due_date')

        action = dbsession.query(Actions).filter_by(case_id=id).one()

        if finding != '' and finding is not None:
            action.finding = finding
            dbsession.commit()
        if corrective_action != '' and corrective_action is not None:
            action.corrective_action = corrective_action
            dbsession.commit()
        if due_date != '' and due_date is not None:
            action.due_date = due_date
            dbsession.commit()

        return redirect(url_for('incidents'))

    else:
        user_profile = (session['username'], session['picture'])
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        incidents = dbsession.query(Incidents.case_num,
                                    func.to_char(Incidents.date_time,
                                                 'FMMonth FMDD, YYYY'),
                                    func.to_char(Incidents.date_time,
                                                 'HH24:MI'),
                                    Incidents.incident_type,
                                    Incidents.incident_cat,
                                    Incidents.injury,
                                    Incidents.property_damage,
                                    Incidents.description,
                                    Incidents.root_cause,
                                    Incidents.user_id). \
            filter_by(case_num=id).first()
        actions = dbsession.query(Actions.corrective_action,
                                  func.to_char(Actions.due_date,
                                               'FMMonth FMDD, YYYY')). \
            filter_by(case_id=id).first()

        creator = int(incidents[9])
        ses_user = int(session['user_id'])

        if 'username' not in session or creator != ses_user:
            flash("Sorry, %s, you are not authorized to edit this incident." %
                  session['username'])
            return redirect('/incidents/')
        else:
            user_profile = (session['username'], session['picture'])
            return render_template('incidents_edit.html',
                                   incidents=incidents,
                                   actions=actions,
                                   user_profile=user_profile)


@app.route('/incidents/delete/<int:id>/', methods=['GET', 'POST'])
def deleteIncident(id):
    """Page to delete an existing incident report"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        action = dbsession.query(Actions).filter_by(case_id=id).first()
        dbsession.delete(action)
        dbsession.commit()

        incident = dbsession.query(Incidents).filter_by(case_num=id).first()
        dbsession.delete(incident)
        dbsession.commit()
        return redirect(url_for('incidents'))
    else:
        # Creates a connection
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()
        incident = dbsession.query(Incidents).filter_by(case_num=id).first()
        creator = int(incident.user_id)
        ses_user = int(session['user_id'])
        if 'username' not in session or creator != ses_user:
            flash("Sorry, %s, you are not authorized to delete this incident." %
                  session['username'])
            return redirect('/incidents/')
        else:
            user_profile = (session['username'], session['picture'])
            return render_template('incidents_delete.html', id=id)
