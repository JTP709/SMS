"""
TODO: main page
- Dashboard
- Generate Report Button
	- Filter reports
	- Select reports
"""

#TODO: create report

from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2

app = Flask(__name__)

def connect(database_name="safety"):
    """Connects to database"""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print ("<error message>")

@app.route('/')
@app.route('/dashboard/')
def dashboard():
	"""Loads the dashboard page"""
	db, cursor = connect()
	# need to add date
	query = """
    		SELECT case_num, incident_cat, description
    			FROM incident
    			WHERE incident.injury = TRUE;
            """
	cursor.execute(query)
	results = cursor.fetchall()
	return render_template('dashboard.html',incidents = results)
	db.close()

@app.route('/reports/')
def reports():
	return "Reports Page for incidents and audits"

@app.route('/newactionitem/')
def newActionItem():
	return "New Action Item Page"

@app.route('/newincident/')
def newIncident():
	return "New Report Page"

@app.route('/newaudit/')
def newAudit():
	return "New Audit Page"

@app.route('/incident/edit/<int:id>')
def editIncident(id):
	return "Edit incident report %s" % id

@app.route('/aduit/edit/<int:id>')
def editAudit(id):
	return "Edit audit page %s" % id

@app.route('/actionitem/edit/<int:id>')
def editActionItem(id):
	return "Edit action item %s" % id

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)