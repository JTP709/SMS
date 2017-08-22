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

def getCaseID
	db, cursor = connect()
	query = ("""
				SELECT case_num
					FROM incident
					ORDER BY case_num desc
					LIMIT 1;
			""")

		cursor.execute(query)
		results = int(cursor.fetchall())


		return str(results)
		db.close()

def incidentActions(case,finding,action)
	db, cursor = connect()
	action_items = ("""
					INSERT INTO action_items (
									case_id,
									finding,
									corrective_action
									)
						VALUES (%s,%s,%s)
					""")
	cursor.execute(action_items, case, finding, action)
	dbclose()

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

@app.route('/incidents/')
def reports():
	return "Reports Page for incidents and audits"

@app.route('/audits/')
def reports():
	return "Reports Page for incidents and audits"

@app.route('/actions/')
def reports():
	return "Reports Page for incidents and audits"

@app.route('/incidents/new/', methods = ['GET','POST'])
def newIncident():
	if request.method == 'POST':
		db, cursor = connect()
		insert = ("""
				INSERT INTO incident (
								date_time,
								incident_type,
								incident_cat,
								injury,
								property_damage,
								description,
								root_cause
								)
					VALUES (%s,%s,%s,%s,%s,%s,%s)
				""")

		date_time = request.form['date_time']
		incident_type = request.form['incident_type']
		incident_cat = request.form['incident_cat']
		injury = request.form['injury']
		property_damage = ['property_damage']
		description = ['description']
		root_cause = ['root_cause']

		cursor.execute(insert, date_time, incident_type, incident_cat, injury, property_damage, description, root_cause)

		#dont forget to make case_id an int
		case_id = getCaseID()
		finding = request.form['finding']
		corrective_action = request.form['corrective_action']

		incidentActions(case_id,finding,corrective_action)

		return redirect(url_for('/incidents/'))
	else:
		return render_template('newincidents.html')
	db.close()

@app.route('/audits/new/', methods = ['GET','POST'])
def newAudit():
	if request.method == 'POST':
		return redirect(url_for(''))
	return "New Audit Page"

@app.route('/actions/new/', methods = ['GET','POST'])
def newActionItem():
	if request.method == 'POST':
		return redirect(url_for(''))
	return "New Action Item Page"

@app.route('/incidents/edit/<int:id>')
def editIncident(id):
	return "Edit incident report %s" % id

@app.route('/aduits/edit/<int:id>')
def editAudit(id):
	return "Edit audit page %s" % id

@app.route('/actions/edit/<int:id>')
def editActionItem(id):
	return "Edit action item %s" % id

@app.route('/incidents/delete/<int:id>')
def editIncident(id):
	return "Delete incident report %s" % id

@app.route('/aduits/delete/<int:id>')
def editAudit(id):
	return "Delete audit page %s" % id

@app.route('/actions/delete/<int:id>')
def editActionItem(id):
	return "Delete action item %s" % id

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)