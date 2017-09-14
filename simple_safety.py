#!/usr/bin/python3

# Import custom functions
from functions import createUser, getUserInfo, getUserID, datetime_handler
from functions import getInjuryRates, getWeather, verifyUser
from functions import login_required, owner_required, check_if_incident_exists
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
#import sys
#print(sys.version)

CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']
APPLICATION_NAME = "Safety Management System"
auth = HTTPBasicAuth()

app = Flask(__name__)

# Authentication


@app.route('/login/')
def showLogin():
    """Routes to Login Page"""
    user_profile = None
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    return render_template('login.html',
                           STATE=state,
                           user_profile=user_profile)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connects to Google Plus OAuth API"""
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data.decode('utf-8')
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the'
                                            'authorization code.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    raw = h.request(url, 'GET')[1]
    result = json.loads(raw.decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(results.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        respones = make_response(json.dumps("Token's user ID doesn't' \
                                            'match the given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does' \
                                            'not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in.
    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.
                                 dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
    # Store the access token in the session for later use.
    session['credentials'] = credentials.access_token
    session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    # See if user exists; if not, make a new one

    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome, '
    output += session['username']
    output += '!</h2>'
    output += '</br>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;" \
    "-moz-border-radius-webkit-border-radius: 150px;" \
    "-moz-border-radius: 150px;"> '
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    """Allows user to logout from Google authentication"""
    access_token = session.get('credentials')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/dashboard/')
    else:
        response = make_response(json.
                                 dumps('Failed to revoke token for given'
                                       'user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    """loads the user profile page"""
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

# Main Page/Dashbaord


@app.route('/')
@app.route('/dashboard/')
def dashboard():
    """Loads the dashboard page"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])
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
    return render_template('dashboard.html',
                           incidents=results,
                           health=health,
                           actions=actions,
                           weather=weather,
                           injury_rate=injury_rate,
                           user_profile=user_profile,
                           manhours=manhours)

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
@login_required
def newIncident():
    """Loads the page to submit a new incident report"""
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
@login_required
def editIncident(id):
    """Page to edit an existing incident report"""
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
@login_required
def deleteIncident(id):
    """Page to delete an existing incident report"""
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
        return render_template('incidents_delete.html', id=id)

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
@login_required
def newAudit():
    """Page to submit a new audit"""
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
@login_required
def editAudit(id):
    """Page to edit an audit"""
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
@login_required
def deleteAudit(id):
    """Page to delete an existing incident report"""
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
        user_profile = (session['username'], session['picture'])
        return render_template('audits_delete.html',
                               id=id,
                               user_profile=user_profile)

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
@login_required
def newActionItem():
    """Page to submit a new action item"""
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
@login_required
def editActionItem(id):
    """Page to edit existing action item"""
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
@login_required
def deleteActionItem(id):
    """Page to delete action item"""
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
        user_profile = (session['username'], session['picture'])
        return render_template('actions_delete.html',
                               id=id,
                               user_profile=user_profile)


@app.route('/actions/close/<int:id>/', methods=['GET', 'POST'])
@login_required
def closeActionItem(id):
    """Page to close action items"""
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

# Resources/Help


@app.route('/resources/')
@app.route('/help/')
def resources():
    """Produces a Help/Resources page"""
    user_profile = None
    if 'username' in session:
        user_profile = (session['username'], session['picture'])
    return render_template('resources.html', user_profile=user_profile)

# JSON API EndPoints


@app.route('/incidents/json/')
def incidentsJSON():
    """Returns all Incidents in the database"""
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Incidents).all()

        return jsonify(Incidents=[i.serialize for i in results])


@app.route('/audits/json')
def auditsJSON():
    """Returns all Audits in the database"""
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Audits).all()

        return jsonify(Audits=[i.serialize for i in results])


@app.route('/actions/json')
def actionsJSON():
    """Returns all Action Items in the database"""
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Actions).all()

        return jsonify(Actions=[i.serialize for i in results])


@app.route('/users/json')
def usersJSON():
    """Returns all users in the database"""
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Users).all()

        return jsonify(Users=[i.serialize for i in results])


@app.route('/incidents/json/<int:id>/')
def incidentsJSONID(id):
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Incidents).filter_by(case_num=id).all()

        return jsonify(Incidents=[i.serialize for i in results])


@app.route('/audits/json/<int:id>/')
def auditsJSONID(id):
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Audits).filter_by(id=id).all()

        return jsonify(Audits=[i.serialize for i in results])


@app.route('/actions/json/<int:id>/')
def actionsJSONID(id):
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Actions).filter_by(id=id).all()

        return jsonify(Actions=[i.serialize for i in results])


@app.route('/users/json/<int:id>/')
def usersJSONID(id):
    if request.method == 'GET':
        # Connect to the database
        con = connect()
        Base.metadata.bind = con
        # Creates a session
        DBSession = sessionmaker(bind=con)
        dbsession = DBSession()

        results = dbsession.query(Users).filter_by(id=id).all()

        return jsonify(Users=[i.serialize for i in results])

if __name__ == '__main__':
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

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
