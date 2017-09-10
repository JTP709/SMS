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