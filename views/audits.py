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

# Audit Manager


@app.route('/audits/')
def audits():
    """Page to view existing audits"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

    results = dbsession.query(Audits.id,
                              func.to_char(Audits.date_time,
                                           'FMMonth FMDD, YYYY'),
                              func.to_char(Audits.date_time,
                                           'HH24:MI'),
                              Audits.type,
                              Audits.ans_1,
                              Audits.ans_2,
                              Audits.ans_3,
                              Actions.finding,
                              Actions.corrective_action). \
        join(Actions, Audits.id == Actions.audit_id). \
        order_by(desc(Audits.id)).all()
    health = []
    # Creates health percentage
    for i in results:
        audit_def = 0.0
        for j in range(len(i)):
            if i[j] is True:
                audit_def = audit_def + 1.0
        audit_perc = int(float(audit_def/3)*100)
        health.append(audit_perc)

    # Fetches Audit Health
    health_rates = []
    audit_results = dbsession.query(Audits.type, Audits.ans_1,
                                    Audits.ans_2, Audits.ans_3).all()
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
    health_rates.append(audit_perc)
    audit_a_perc = int(float(audit_a_def/a_total*100))
    health_rates.append(audit_a_perc)
    audit_b_perc = int(float(audit_b_def/b_total*100))
    health_rates.append(audit_b_perc)
    audit_h_perc = int(float(audit_h_def/h_total*100))
    health_rates.append(audit_h_perc)

    length = len(results)

    return render_template('audits.html',
                           audits=results,
                           length=length,
                           health=health,
                           health_rates=health_rates,
                           user_profile=user_profile)
    db.close()


@app.route('/audits/new/', methods=['GET', 'POST'])
def newAudit():
    """Page to submit a new audit"""
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
        audit_type = request.form['audit_type']
        # Auto populates the question field based on audit type selected.
        if audit_type == 'Behavior':
            question_1 = 'Was the employee wearing their PPE?'
            question_2 = 'Does the area have designated locations \
                for all carts, tools, pallets, inventory, and \
                non-inventory items?'
            question_3 = 'Are all barrels in good condition?'
        if audit_type == 'Area Organization':
            question_1 = 'Was the employee using proper lifting techniques?'
            question_2 = 'Are all carts, pallets, tools, and items in a \
                designated location?'
            question_3 = 'Are all barrels properly labelled?'
        if audit_type == 'HAZWASTE':
            question_1 = "Was the employee's work area clean?"
            question_2 = 'Is the area clean and free from trip hazards?'
            question_3 = 'Are the appropriate HAZWASTE items \
                stored in the proper container?'

        audits = Audits(date_time=request.form['date_time'],
                        type=audit_type,
                        ans_1=request.form['answer_1'],
                        ans_2=request.form['answer_2'],
                        ans_3=request.form['answer_3'],
                        que_1=question_1,
                        que_2=question_2,
                        que_3=question_3,
                        user_id=user_id)
        dbsession.add(audits)
        dbsession.commit()

        getaudit_id = dbsession.query(Audits.id). \
            order_by(desc(Audits.id)).first()
        audit_id = getaudit_id[0]
        ca = request.form['corrective_action']
        action_items = Actions(finding=request.form['description'],
                               corrective_action=ca,
                               due_date=request.form['due_date'],
                               open_close='t',
                               user_id=user_id,
                               audit_id=audit_id)

        dbsession.add(action_items)
        dbsession.commit()

        return redirect(url_for('audits'))
    else:
        user_profile = (session['username'], session['picture'])
        return render_template('audits_new.html',
                               user_profile=user_profile)


@app.route('/audits/edit/<int:id>/', methods=['GET', 'POST'])
def editAudit(id):
    """Page to edit an audit"""
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
        answer_1 = request.form.get('ansewr_1')
        answer_2 = request.form.get('ansewr_2')
        answer_3 = request.form.get('ansewr_3')

        data = dbsession.query(Audits).filter_by(id=id).one()

        # Creates a seperate insert execution per input generated.

        if date_time != '' and date_time is not None:
            data.date_time = date_time
            dbsession.commit()
        if answer_1 != '' and answer_1 is not None:
            data.ans_1 = answer_1
            dbsession.commit()
        if answer_2 != '' and answer_2 is not None:
            data.ans_2 = answer_2
        if answer_3 != '' and answer_3 is not None:
            data.ans_3 = answer_3

        finding = request.form.get('description')
        corrective_action = request.form.get('corrective_action')
        due_date = request.form.get('due_date')

        action = dbsession.query(Actions).filter_by(audit_id=id).one()

        if finding != '' and finding is not None:
            action.finding = finding
            dbsession.commit()
        if corrective_action != '' and corrective_action is not None:
            action.corrective_action = corrective_action
            dbsession.commit()
        if due_date != '' and due_date is not None:
            action.due_date = due_date
            dbsession.commit()

        return redirect(url_for('audits'))

    else:
        user_profile = (session['username'], session['picture'])
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Audits.id,
                                  func.to_char(Audits.date_time,
                                               'FMMonth FMDD, YYYY'),
                                  func.to_char(Audits.date_time,
                                               'HH24:MI'),
                                  Audits.type,
                                  Audits.que_1,
                                  Audits.que_2,
                                  Audits.que_3,
                                  Audits.ans_1,
                                  Audits.ans_2,
                                  Audits.ans_3,
                                  Actions.id,
                                  Actions.finding,
                                  Actions.corrective_action,
                                  Actions.due_date,
                                  Actions.user_id,
                                  Audits.user_id).filter_by(id=id). \
            join(Actions,
                 Audits.id == Actions.audit_id).first()
        print(results[14])
        print(session['user_id'])

        creator = int(results[14])
        ses_user = int(session['user_id'])

        if 'username' not in session or creator != ses_user:
            flash("Sorry, %s, you are not authorized to edit this Audit."
                  % session['username'])
            return redirect('/audits/')
        else:
            return render_template('audits_edit.html',
                                   audits=results,
                                   user_profile=user_profile)
        db.close()


@app.route('/audits/delete/<int:id>/', methods=['GET', 'POST'])
def deleteAudit(id):
    """Page to delete an existing incident report"""
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        action = dbsession.query(Actions).filter_by(audit_id=id).first()
        dbsession.delete(action)
        dbsession.commit()

        audit = dbsession.query(Audits).filter_by(id=id).first()
        dbsession.delete(audit)
        dbsession.commit()

        return redirect(url_for('audits'))
    else:
        # Creates a connection
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()
        audit = dbsession.query(Audits).filter_by(id=id).first()
        creator = int(audit.user_id)
        ses_user = int(session['user_id'])
        if 'username' not in session or creator != ses_user:
            flash("Sorry, %s, you are not authorized to delete this incident." %
                  session['username'])
            return redirect('/audits/')
        else:
            user_profile = (session['username'], session['picture'])
            return render_template('audits_delete.html',
                                   id=id,
                                   user_profile=user_profile)
