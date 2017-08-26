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

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response, flash
import psycopg2
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
#from functions import connect, audit_health, audit_totals, getCaseID, incidentActions

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']
APPLICATION_NAME = "Safety Management System"

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

def getUserIDNum():
	db, cursor = connect()
	query = ("""
				SELECT id
					FROM users
					ORDER BY id desc
					LIMIT 1;
			""")

	cursor.execute(query)
	results = cursor.fetchone()
	results_a = int(results[0])

	return str(results_a)
	db.close()

def createUser(session):
	db, cursor = connect()
	insert = ("""
			INSERT INTO users (
							id,
							name,
							email,
							picture
							)
				VALUES (%s,%s,%s,%s)
			""")
	case_id = getUserIDNum()
	new_id = str(int(case_id)+1)
	name = session['username']
	email = session['email']
	picture = session['picture']
		
	data = (new_id, name, email, picture)

	cursor.execute(insert, data)
	db.commit()
	db.close()
	return new_id

def getUserInfo(id):
	db, cursor = connect()
	query = """
			SELECT id,
					name,
					email,
					picture,
					position
				FROM users
				WHERE id = %s;
			"""
	data = (str(id),)
	cursor.execute(query, data)
	results = cursor.fetchone()
	return results
	db.close()

def getUserID(email):
	db, cursor = connect()
	query = """
			SELECT id
				FROM users
				WHERE email = %s;
			"""
	data = (email,)
	cursor.execute(query, data)
	results = cursor.fetchone()
	return results
	db.close()

app = Flask(__name__)

@app.route('/login/')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	session['state'] = state
	return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	if request.args.get('state') != session['state']:
		response = make_response(json.dumps('Invalid state'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	code = request.data.decode('utf-8')
	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(results.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		respones = make_response(json.dumps("Token's user ID doesn't match the given user ID"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's."), 401)
		print("Token's client ID does not match app's.")
		response.headers['Content-Type'] = 'application/json'
		return response
	# Check to see if user is already logged in.
	stored_credentials = session.get('credentials')
	stored_gplus_id = session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
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
	output += '<h1>Welcome, '
	output += session['username']
	output += '!</h1>'
	output += '<img src="'
	output += session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	print(credentials)
	print(credentials.access_token)
	flash("you are now logged in as %s" % session['username'])
	print("done!")
	return output

@app.route('/gdisconnect/')
def gdisconnect():
    access_token = session.get('credentials')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session['credentials']
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
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

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
	db.close()
	return render_template('dashboard.html',incidents = results, health = health, actions = actions)

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
	if 'username' not in session:
		return redirect('/login')
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
								root_cause,
								user_id
								)
					VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
		user_id	 = getUserID(session['email'])

		data = (new_id, date_time, incident_type, incident_cat, injury, property_damage, description, root_cause, user_id)

		#print(date_time, incident_type, incident_cat, injury, property_damage, description, root_cause)

		cursor.execute(insert, data)

		action_items = ("""
					INSERT INTO action_items (
									case_id,
									finding,
									corrective_action,
									due_date,
									open_close,
									user_id
									)
						VALUES (%s,%s,%s,%s,%s,%s)
					""")

		finding = request.form['description']
		corrective_action = request.form['corrective_action']
		due_date = request.form['due_date']
		open_close = 't'
		user_id	 = session['user_id']

		data_a = (new_id, finding, corrective_action, due_date, open_close, user_id)

		cursor.execute(action_items, data_a)
		db.commit()
		db.close()

		return redirect(url_for('incidents'))
	else:
		return render_template('incidents_new.html')

@app.route('/incidents/edit/<int:id>/', methods = ['GET','POST'])
def editIncident(id):
	if 'username' not in session:
		return redirect('/login')
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
		    			a.due_date,
		    			i.user_id
	    			FROM incident as i, action_items as a
	    			WHERE i.case_num = a.case_id AND i.case_num = %s;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		creator = getUserInfo(str(results[0][11]))
		if 'username' not in session or int(creator[0]) != int(session['user_id']):
			output = ''
			output += "<h1>I'm sorry, "
			output += session['username']
			output += '! You are not authorized to edit this incident.</h1>'
			output += "Please return to the <a href ='/incidients/'>Incidents Page.</a>"
			return output 
		else:
			return render_template('incidents_edit.html',incidents = results)
		db.close()

@app.route('/incidents/delete/<int:id>/', methods = ['GET','POST'])
def deleteIncident(id):
	if 'username' not in session:
		return redirect('/login')
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
	if 'username' not in session:
		return redirect('/login')
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
								ans_3,
								user_id
								)
					VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
				""")
		audit_id = getAuditID()
		new_id = str(int(audit_id)+1)
		date_time = request.form['date_time']
		audit_type = request.form['audit_type']
		answer_1 = request.form['answer_1']
		answer_2 = request.form['answer_2']
		answer_3 = request.form['answer_3']
		user_id	 = getUserID(session['email'])

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

		data = (new_id, date_time, audit_type, question_1, question_2, question_3, answer_1, answer_2, answer_3, user_id)

		cursor.execute(insert, data)

		action_items = ("""
					INSERT INTO action_items (
									audit_id,
									finding,
									corrective_action
									due_date,
									open_close,
									user_id
									)
						VALUES (%s,%s,%s,%s,%s,%s)
					""")

		finding = request.form['description']
		corrective_action = request.form['corrective_action']
		due_date = request.form['due_date']
		open_close = 't'
		user_id	 = session['user_id']

		data_a = (new_id, finding, corrective_action, due_date, open_close)

		cursor.execute(action_items, data_a)
		db.commit()
		db.close()

		return redirect(url_for('audits'))
	else:
		return render_template('audits_new.html')

@app.route('/audits/edit/<int:id>/', methods = ['GET','POST'])
def editAudit(id):
	if 'username' not in session:
		return redirect('/login')
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
	    			i.due_date,
	    			i.user_id
    			FROM audit as a, action_items as i
    			WHERE a.id = i.audit_id
    			ORDER BY a.id desc;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		creator = getUserInfo(str(results[0][14]))
		if 'username' not in session or int(creator[0]) != int(session['user_id']):
			output = ''
			output += "<h1>I'm sorry, "
			output += session['username']
			output += '! You are not authorized to edit this audit.</h1>'
			output += "Please return to the <a href ='/audits/'>Incidents Page.</a>"
			return output 
		else:
			return render_template('audits_edit.html',audits = results)
		db.close()

@app.route('/audits/delete/<int:id>/', methods = ['GET','POST'])
def deleteAudit(id):
	if 'username' not in session:
		return redirect('/login')
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
	if 'username' not in session:
		return redirect('/login')
	if request.method == 'POST':
		db, cursor = connect()
		insert = ("""
				INSERT INTO action_items (
								id,
								date_time,
								finding,
								corrective_action,
								due_date,
								open_close,
								user_id
								)
					VALUES (%s,%s,%s,%s,%s,%s,%s)
				""")
		case_id = getActionsID()
		new_id = str(int(case_id)+1)
		date_time = request.form['date_time']
		finding = request.form['finding']
		corrective_action = request.form['corrective_action']
		due_date = request.form['due_date']
		open_close = 't'
		user_id	 = getUserID(session['email'])

		data = (new_id, date_time, finding, corrective_action, due_date, open_close)

		cursor.execute(insert, data)
		
		db.commit()
		db.close()

		return redirect(url_for('actions'))
	else:
		return render_template('actions_new.html')

@app.route('/actions/edit/<int:id>/', methods = ['GET','POST'])
def editActionItem(id):
	if 'username' not in session:
		return redirect('/login')
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
    				due_date,
    				user_id
    			FROM action_items
    			WHERE id = %s;
	            """
		data = (str(id),)
		cursor.execute(query, data)
		results = cursor.fetchall()
		creator = getUserInfo(str(results[0][8]))
		if 'username' not in session or int(creator[0]) != int(session['user_id']):
			output = ''
			output += "<h1>I'm sorry, "
			output += session['username']
			output += '! You are not authorized to edit this action item.</h1>'
			output += "Please return to the <a href ='/actions/'>Incidents Page.</a>"
			return output 
		else:
			return render_template('actions_edit.html',actions = results)
		db.close()

@app.route('/actions/delete/<int:id>/', methods = ['GET','POST'])
def deleteActionItem(id):
	if 'username' not in session:
		return redirect('/login')
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
	if 'username' not in session:
		return redirect('/login')
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

@app.route('/reports/')
def reports():
	return "This page will be used to generate custom reports and injury/incident trends."

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)