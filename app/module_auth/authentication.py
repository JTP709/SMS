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
        print("Token's client ID does not match app's.")
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
    print("done!")
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    """Allows user to logout from Google authentication"""
    access_token = session.get('credentials')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
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