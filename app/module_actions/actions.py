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

# Action Item Manager


@app.route('/actions/')
def actions():
    """Page to view open action items"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

    results = dbsession.query(Actions.id,
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
        order_by(desc(Actions.id)).all()

    length = len(results)

    return render_template('actions.html',
                           actions=results,
                           length=length,
                           user_profile=user_profile)


@app.route('/actions/new/', methods=['GET', 'POST'])
def newActionItem():
    """Page to submit a new action item"""
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

        actions = Actions(date_time=request.form['date_time'],
                          finding=request.form['finding'],
                          corrective_action=request.form['corrective_action'],
                          due_date=request.form['due_date'],
                          open_close='t',
                          user_id=user_id)
        dbsession.add(actions)
        dbsession.commit()

        return redirect(url_for('actions'))
    else:
        user_profile = (session['username'], session['picture'])
        return render_template('actions_new.html', user_profile=user_profile)


@app.route('/actions/edit/<int:id>/', methods=['GET', 'POST'])
def editActionItem(id):
    """Page to edit existing action item"""
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
        finding = request.form.get('finding')
        corrective_action = request.form.get('corrective_action')
        due_date = request.form.get('due_date')

        data = dbsession.query(Actions).filter_by(id=id).one()

        if date_time != '' and date_time is not None:
            data.date_time = date_time
            dbsession.commit()
        if finding != '' and finding is not None:
            data.finding = finding
            dbsession.commit()
        if corrective_action != '' and corrective_action is not None:
            data.corrective_action = corrective_action
            dbsession.commit()
        if due_date != '' and due_date is not None:
            data.due_date = due_date
            dbsession.commit()

        return redirect(url_for('actions'))

    else:
        user_profile = (session['username'], session['picture'])
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

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
                                  Actions.user_id). \
            filter_by(id=id).first()

        creator = int(actions[8])
        ses_user = int(session['user_id'])

        if 'username' not in session or creator != ses_user:
            flash("Sorry, %s, you are not authorized to edit this \
                  action item." % session['username'])
            return redirect('/actions/')
        else:
            return render_template('actions_edit.html',
                                   actions=actions,
                                   user_profile=user_profile)
        db.close()


@app.route('/actions/delete/<int:id>/', methods=['GET', 'POST'])
def deleteActionItem(id):
    """Page to delete action item"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        action = dbsession.query(Actions).filter_by(id=id).first()
        dbsession.delete(action)
        dbsession.commit()
        return redirect(url_for('actions'))
    else:
        # Creates a connection
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()
        action = dbsession.query(Actions).filter_by(id=id).first()
        creator = int(action.user_id)
        ses_user = int(session['user_id'])
        if 'username' not in session or creator != ses_user:
            flash("Sorry, %s, you are not authorized to delete this incident." %
                  session['username'])
            return redirect('/actions/')
        else:
            user_profile = (session['username'], session['picture'])
            return render_template('actions_delete.html',
                                   id=id,
                                   user_profile=user_profile)


@app.route('/actions/close/<int:id>/', methods=['GET', 'POST'])
def closeActionItem(id):
    """Page to close action items"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        close = dbsession.query(Actions).filter_by(id=id).one()
        close.open_close = 'f'
        dbsession.commit()

        return redirect(url_for('actions'))
    else:
        user_profile = (session['username'], session['picture'])
        return render_template('actions_close.html',
                               id=id,
                               user_profile=user_profile)
