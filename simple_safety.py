"""
TODO: main page
- Action Item Update
 - Incident Report "finding" auto populate bug
 - Add date to action items
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

def getAuditID():
	db, cursor = connect()
	query = ("""
				SELECT id
					FROM audit
					ORDER BY id desc
					LIMIT 1;
			""")

	cursor.execute(query)
	results = cursor.fetchone()
	results_a = int(results[0])

	return str(results_a)
	db.close()

def getActionsID():
	db, cursor = connect()
	query = ("""
				SELECT id
					FROM action_items
					ORDER BY id desc
					LIMIT 1;
			""")

	cursor.execute(query)
	results = cursor.fetchone()
	results_a = int(results[0])

	return str(results_a)
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

	query = """
    		SELECT id,
    				to_char(date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(date_time, 'HH12:MI'), 
    				case_id,
    				audit_id,
    				finding,
    				corrective_action,
    				to_char(due_date, 'FMMonth FMDD, YYYY'),
    				open_close
    			FROM action_items
    			ORDER BY date_time
    			LIMIT 5;
            """
	cursor.execute(query)
	actions = cursor.fetchall()
			
	length = len(results)

	return render_template('dashboard.html',incidents = results, health = health, actions = actions)
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
									corrective_action,
									due_date,
									open_close
									)
						VALUES (%s,%s,%s,%s,%s)
					""")

		finding = request.form['description']
		corrective_action = request.form['corrective_action']
		due_date = request.form['due_date']
		open_close = 't'

		data_a = (new_id, finding, corrective_action, due_date, open_close)

		cursor.execute(action_items, data_a)
		db.commit()
		db.close()

		return redirect(url_for('incidents'))
	else:
		return render_template('incidents_new.html')

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
		due_date = request.form.get('due_date')

		action_query = [[date_time,'date_time'],[finding,'finding'],[corrective_action,'corrective_action'], [due_date, 'due_date']]

		for j in range(len(action_query)):
			if action_query[j][0] != '' and action_query[j][0] != None:
				newActionData = (action_query[j][0],case_id[0])
				insertAction = ("UPDATE action_items SET "+action_query[j][1]+" = %s WHERE case_id = %s")
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
		    			a.corrective_action,
		    			a.due_date
	    			FROM incident as i, action_items as a
	    			WHERE i.case_num = a.case_id AND i.case_num = %s;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		return render_template('incidents_edit.html',incidents = results)
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
		return render_template('incidents_delete.html', id = id)

@app.route('/audits/')
def audits():
	db, cursor = connect()
	# need to add date
	query = """
    		SELECT a.id,
    				to_char(a.date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(a.date_time, 'HH12:MI'), 
	    			a.type,
	    			a.ans_1,
	    			a.ans_2,
	    			a.ans_3,
	    			i.id,
	    			i.finding,
	    			i.corrective_action
    			FROM audit as a, action_items as i
    			WHERE a.id = i.audit_id
    			ORDER BY a.id desc;
            """
	cursor.execute(query)
	results = cursor.fetchall()
	health = []
	for i in results:
		audit_def = 0.0
		for j in range(len(i)):
			if i[j] == False:
				audit_def = audit_def + 1.0
		audit_perc = int(float(audit_def/3)*100)
		health.append(audit_perc)
		
	length = len(results)

	return render_template('audits.html',audits = results, length = length, health = health)
	db.close()

@app.route('/audits/new/', methods = ['GET','POST'])
def newAudit():
	if request.method == 'POST':
		db, cursor = connect()
		insert = ("""
				INSERT INTO audit (
								id,
								date_time,
								type,
								que_1,
								que_2,
								que_3,
								ans_1,
								ans_2,
								ans_3
								)
					VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
				""")
		audit_id = getAuditID()
		new_id = str(int(audit_id)+1)
		date_time = request.form['date_time']
		audit_type = request.form['audit_type']
		answer_1 = request.form['answer_1']
		answer_2 = request.form['answer_2']
		answer_3 = request.form['answer_3']

		if audit_type == 'Behavior':
			question_1 = 'Was the employee wearing their PPE?'
			question_2 = 'Does the area have designated locations for all carts, tools, pallets, inventory, and non-inventory items?'
			question_3 = 'Are all barrels in good condition?'
		if audit_type == 'Area Organization':
			question_1 = 'Was the employee using proper lifting techniques?'
			question_2 = 'Are all carts, pallets, tools, and items in a designated location?'
			question_3 = 'Are all barrels properly labelled?'
		if audit_type == 'HAZWASTE':
			question_1 = "Was the employee's work area clean?"
			question_2 = 'Is the area clean and free from trip hazards?'
			question_3 = 'Are the appropriate HAZWASTE items stored in the proper container?'

		data = (new_id, date_time, audit_type, question_1, question_2, question_3, answer_1, answer_2, answer_3)

		cursor.execute(insert, data)

		action_items = ("""
					INSERT INTO action_items (
									audit_id,
									finding,
									corrective_action
									due_date,
									open_close
									)
						VALUES (%s,%s,%s,%s,%s)
					""")

		finding = request.form['description']
		corrective_action = request.form['corrective_action']
		due_date = request.form['due_date']
		open_close = 't'

		data_a = (new_id, finding, corrective_action, due_date, open_close)

		cursor.execute(action_items, data_a)
		db.commit()
		db.close()

		return redirect(url_for('audits'))
	else:
		return render_template('audits_new.html')

@app.route('/audits/edit/<int:id>/', methods = ['GET','POST'])
def editAudit(id):
	if request.method == 'POST':
		db, cursor = connect()
		
		audit_id = (int(id),)
		date_time = request.form.get('date_time')
		audit_type = request.form.get('audit_type')
		question_1 = request.form.get('question_1')
		question_2 = request.form.get('question_2')
		question_3 = request.form.get('question_3')
		answer_1 = request.form.get('ansewr_1')
		answer_2 = request.form.get('ansewr_2')
		answer_3 = request.form.get('ansewr_3')

		query = [[date_time,'date_time'],[audit_type,'type'],[question_1,'question_1'],[question_2,'question_2'],[question_3,'question_3'],[answer_1,'answer_1'],[answer_2,'answer_2'],[answer_3,'answer_3']]

		for i in range(len(query)):
			if query[i][0] != '' and query[i][0] != None:
				newdata = (query[i][0],audit_id[0])
				insert = ("UPDATE audit SET "+query[i][1]+" = %s WHERE id = %s")
				cursor.execute(insert,newdata)
		
		finding = request.form.get('description')
		corrective_action = request.form.get('corrective_action')
		due_date = request.form.get('due_date')

		action_query = [[date_time,'date_time'],[finding,'finding'],[corrective_action,'corrective_action'], [due_date, 'due_date']]

		for j in range(len(action_query)):
			if action_query[j][0] != '' and action_query[j][0] != None:
				newActionData = (action_query[j][0],audit_id[0])
				insertAction = ("UPDATE action_items SET "+action_query[j][1]+" = %s WHERE audit_id = %s")
				cursor.execute(insertAction,newActionData)

		db.commit()
		db.close()

		return redirect(url_for('audits'))

	else:
		db, cursor = connect()
		
		query = """
	    		SELECT a.id,
    				to_char(a.date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(a.date_time, 'HH12:MI'), 
	    			a.type,
	    			a.que_1,
	    			a.que_2,
	    			a.que_3,
	    			a.ans_1,
	    			a.ans_2,
	    			a.ans_3,
	    			i.id,
	    			i.finding,
	    			i.corrective_action,
	    			i.due_date
    			FROM audit as a, action_items as i
    			WHERE a.id = i.audit_id
    			ORDER BY a.id desc;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		return render_template('audits_edit.html',audits = results)
		db.close()

@app.route('/audits/delete/<int:id>/', methods = ['GET','POST'])
def deleteAudit(id):
	if request.method == 'POST':
		db, cursor = connect()
		delete = """
				DELETE FROM action_items
				WHERE audit_id = %s;
				DELETE FROM audit
				WHERE id = %s;
				"""
		case = (str(id),str(id))
		cursor.execute(delete,case)
		db.commit()
		db.close()
		return redirect(url_for('audits'))
	else:
		return render_template('audits_delete.html', id = id)

@app.route('/actions/')
def actions():
	db, cursor = connect()
	
	query = """
    		SELECT id,
    				to_char(date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(date_time, 'HH12:MI'), 
    				case_id,
    				audit_id,
    				finding,
    				corrective_action,
    				to_char(due_date, 'FMMonth FMDD, YYYY'),
    				open_close
    			FROM action_items
    			ORDER BY id desc;
            """
	cursor.execute(query)
	results = cursor.fetchall()
			
	length = len(results)

	return render_template('actions.html',actions = results, length = length)
	db.close()

@app.route('/actions/new/', methods = ['GET','POST'])
def newActionItem():
	if request.method == 'POST':
		db, cursor = connect()
		insert = ("""
				INSERT INTO action_items (
								id,
								date_time,
								finding,
								corrective_action,
								due_date,
								open_close
								)
					VALUES (%s,%s,%s,%s,%s,%s)
				""")
		case_id = getActionsID()
		new_id = str(int(case_id)+1)
		date_time = request.form['date_time']
		finding = request.form['finding']
		corrective_action = request.form['corrective_action']
		due_date = request.form['due_date']
		open_close = 't'

		data = (new_id, date_time, finding, corrective_action, due_date, open_close)

		cursor.execute(insert, data)
		
		db.commit()
		db.close()

		return redirect(url_for('actions'))
	else:
		return render_template('actions_new.html')

@app.route('/actions/edit/<int:id>/', methods = ['GET','POST'])
def editActionItem(id):
	if request.method == 'POST':
		db, cursor = connect()
		
		case_id = (int(id),)
		date_time = request.form.get('date_time')
		finding = request.form.get('finding')
		corrective_action = request.form.get('corrective_action')
		due_date = request.form.get('due_date')

		query = [[date_time,'date_time'],[finding,'finding'],[corrective_action,'corrective_action'], [due_date, 'due_date']]

		for i in range(len(query)):
			if query[i][0] != '' and query[i][0] != None:
				newdata = (query[i][0],case_id[0])
				insert = ("UPDATE action_items SET "+query[i][1]+" = %s WHERE id = %s")
				cursor.execute(insert,newdata)

		db.commit()
		db.close()

		return redirect(url_for('actions'))

	else:
		db, cursor = connect()
		
		query = """
	    		SELECT id,
    				to_char(date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(date_time, 'HH12:MI'), 
    				case_id,
    				audit_id,
    				finding,
    				corrective_action,
    				due_date
    			FROM action_items
    			WHERE id = %s;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		return render_template('actions_edit.html',actions = results)
		db.close()

@app.route('/actions/delete/<int:id>/', methods = ['GET','POST'])
def deleteActionItem(id):
	if request.method == 'POST':
		db, cursor = connect()
		delete = """
				DELETE FROM action_items
				WHERE id = %s;
				"""
		case = (str(id),)
		cursor.execute(delete,case)
		db.commit()
		db.close()
		return redirect(url_for('actions'))
	else:
		return render_template('actions_delete.html', id = id)

@app.route('/actions/close/<int:id>/', methods = ['GET','POST'])
def closeActionItem(id):
	if request.method == 'POST':
		db, cursor = connect()
		close = """
				UPDATE action_items
					SET open_close = 'f'
					WHERE id = %s
				"""
		action_id = (int(id),)
		cursor.execute(close, action_id)
		db.commit()
		db.close()
		return redirect(url_for('actions'))
	else:
		return render_template('actions_close.html', id = id)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)