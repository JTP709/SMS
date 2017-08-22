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

def audit_health():
	db, cursor = connect()
	query = """
    		SELECT count(*) as num
    			FROM audit
    			WHERE ans_1 = FALSE OR
    				ans_2 = FALSE OR
    				ans_3 = FALSE
            """
	cursor.execute(query)
	results = cursor.fetchone()
	return results
	db.close()

def audit_totals():
	db, cursor = connect()
	query = """
			SELECT count(*) as num
				FROM audit
			"""

	cursor.execute(query)
	results = cursor.fetchone()

	return results
	db.close()

@app.route('/')
@app.route('/dashboard/')
def dashboard():
	"""Loads the dashboard page"""
	db, cursor = connect()
	# need to add date
	incident_query = """
    		SELECT to_char(date_time, 'FMMonth FMDD, YYYY'),
    			to_char(date_time, 'HH12:MI'),
    			case_num, incident_cat, description
    			FROM incident
    			WHERE incident.injury = TRUE
    			ORDER BY date_time desc;
            """
	cursor.execute(incident_query)
	results = cursor.fetchall()

	audit_query = audit_health()
	audit_query_t = audit_totals()
	health = round(float(float(audit_query[0])/float(audit_query_t[0]))*100,2)

	return render_template('dashboard.html',incidents = results, health = health)
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