"""
TODO: main page
- Dashboard
	- 
- Generate Report Button
	- Filter reports
	- Select reports
- Add OAuth with users that can generate seperate information for their specific site.
	- Local Weather API
		- Severe Weather Notifications sent to e-mail
"""

#TODO: create report

from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
#from functions import connect, audit_health, audit_totals, getCaseID, incidentActions

def connect(database_name="safety"):
    """Connects to database"""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print ("Could not connect to the database.")

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

def getCaseID():
	db, cursor = connect()
	query = ("""
				SELECT case_num
					FROM incident
					ORDER BY case_num desc
					LIMIT 1;
			""")

	cursor.execute(query)
	results = cursor.fetchone()
	results_i = int(results[0])

	return str(results_i)
	db.close()

app = Flask(__name__)

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
def incidents():
	db, cursor = connect()
	# need to add date
	incident_query = """
    		SELECT case_num,
    				to_char(date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(date_time, 'HH12:MI'), 
	    			incident_type, 
	    			incident_cat, 
	    			injury, 
	    			property_damage,
	    			description,
	    			root_cause
    			FROM incident
    			ORDER BY case_num desc;
            """
	cursor.execute(incident_query)
	results = cursor.fetchall()
	length = len(results)

	return render_template('incidents.html',incidents = results, length = length)
	db.close()

@app.route('/incidents/new/', methods = ['GET','POST'])
def newIncident():
	if request.method == 'POST':
		db, cursor = connect()
		insert = ("""
				INSERT INTO incident (
								case_num,
								date_time,
								incident_type,
								incident_cat,
								injury,
								property_damage,
								description,
								root_cause
								)
					VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
				""")
		case_id = getCaseID()
		new_id = str(int(case_id)+1)
		date_time = request.form['date_time']
		incident_type = request.form['incident_type']
		incident_cat = request.form['incident_cat']
		injury = request.form['injury']
		property_damage = request.form['property_damage']
		description = request.form['description']
		root_cause = request.form['root_cause']

		data = (new_id, date_time, incident_type, incident_cat, injury, property_damage, description, root_cause)

		#print(date_time, incident_type, incident_cat, injury, property_damage, description, root_cause)

		cursor.execute(insert, data)
		print(data)

		action_items = ("""
					INSERT INTO action_items (
									case_id,
									finding,
									corrective_action
									)
						VALUES (%s,%s,%s)
					""")

		finding = request.form['description']
		corrective_action = request.form['corrective_action']

		data_a = (new_id, finding, corrective_action)

		cursor.execute(action_items, data_a)
		db.commit()
		db.close()

		return redirect(url_for('incidents'))
	else:
		return render_template('newincidents.html')

@app.route('/incidents/edit/<int:id>/', methods = ['GET','POST'])
def editIncident(id):
	if request.method == 'POST':
		db, cursor = connect()
		
		case_id = (int(id),)
		date_time = request.form.get('date_time')
		incident_type = request.form.get('incident_type')
		incident_cat = request.form.get('incident_cat')
		injury = request.form.get('injury')
		property_damage = request.form.get('property_damage')
		description = request.form.get('description')
		root_cause = request.form.get('root_cause')

		query = [[date_time,'date_time'],[incident_type,'incident_type'],[incident_cat,'incident_cat'],[injury,'injury'],[property_damage,'property_damage'],[description, 'description'], [root_cause,'root_cause']]

		for i in range(len(query)):
			if query[i][0] != '' and query[i][0] != None:
				newdata = (query[i][0],case_id[0])
				insert = ("UPDATE incident SET "+query[i][1]+" = %s WHERE case_num = %s")
				cursor.execute(insert,newdata)
		
		finding = request.form.get('description')
		corrective_action = request.form.get('corrective_action')

		action_query = [[finding,'finding'],[corrective_action,'corrective_action']]

		for j in range(len(action_query)):
			if action_query[j][0] != '' and action_query[j][0] != None:
				newActionData = (action_query[j][0],case_id[0])
				insertAction = ("UPDATE action_items SET "+action_query[j][1]+" = %s WHERE case_num = %s")
				cursor.execute(insertAction,newActionData)

		db.commit()
		db.close()

		return redirect(url_for('incidents'))

	else:
		db, cursor = connect()
		
		query = """
	    		SELECT i.case_num,
	    				to_char(i.date_time, 'FMMonth FMDD, YYYY'),
		    			to_char(i.date_time, 'HH12:MI'),
		    			i.incident_type, 
		    			i.incident_cat, 
		    			i.injury, 
		    			i.property_damage,
		    			i.description,
		    			i.root_cause,
		    			a.corrective_action
	    			FROM incident as i, action_items as a
	    			WHERE i.case_num = a.case_id AND i.case_num = %s;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		return render_template('incident_id.html',incidents = results)
		db.close()

@app.route('/incidents/delete/<int:id>/', methods = ['GET','POST'])
def deleteIncident(id):
	if request.method == 'POST':
		db, cursor = connect()
		delete = """
				DELETE FROM action_items
				WHERE case_id = %s;
				DELETE FROM incident
				WHERE case_num = %s;
				"""
		case = (str(id),str(id))
		cursor.execute(delete,case)
		db.commit()
		db.close()
		return redirect(url_for('incidents'))
	else:
		return render_template('incident_delete.html', id = id)

@app.route('/audits/')
def audits():
	return "Reports Page for incidents and audits"

@app.route('/audits/new/', methods = ['GET','POST'])
def newAudit():
	if request.method == 'POST':
		return redirect(url_for(''))
	return "New Audit Page"

@app.route('/actions/')
def actions():
	return "Reports Page for incidents and audits"

@app.route('/actions/new/', methods = ['GET','POST'])
def newActionItem():
	if request.method == 'POST':
		return redirect(url_for(''))
	return "New Action Item Page"

@app.route('/aduits/edit/<int:id>')
def editAudit(id):
	return "Edit audit page %s" % id

@app.route('/actions/edit/<int:id>')
def editActionItem(id):
	return "Edit action item %s" % id

@app.route('/aduits/delete/<int:id>')
def deleteAudit(id):
	return "Delete audit page %s" % id

@app.route('/actions/delete/<int:id>')
def deleteActionItem(id):
	return "Delete action item %s" % id

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)