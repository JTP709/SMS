"""
TODO: main page
- Dashboard
- Generate Report Button
	- Filter reports
	- Select reports
"""

#TODO: create report

from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/dashboard/')
def dashboard():
	return "Main Dashboard Page"

@app.route('/reports/')
def dashboard():
	return "Reports Page for incidents and audits"

@app.route('/newactionitem/')
def dashboard():
	return "New Action Item Page"

@app.route('/newincident/')
def dashboard():
	return "New Report Page"

@app.route('/newaudit/')
def dashboard():
	return "New Audit Page"

@app.route('/incident/edit/<int:id>')
def dashboard():
	return "Edit incident report %s" % id

@app.route('/aduit/edit/<int:id>')
def dashboard():
	return "Edit audit page %s" % id

@app.route('/actionitem/edit/<int:id>')
def dashboard():
	return "Edit action item %s" % id

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)