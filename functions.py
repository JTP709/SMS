import psycopg2, datetime, json, httplib2

def connect(database_name="safety"):
    """Connects to database"""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print ("Could not connect to the database.")

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

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def getWeather():
	# http://api.openweathermap.org/data/2.5/forecast?id=4508722&APPID=00b1eab8137a0b1d81025d667dbb2f17
	# app_id = 00b1eab8137a0b1d81025d667dbb2f17
	# City ID for Cincinnati, OH
	# city_id = 4508722
	url = 'http://api.openweathermap.org/data/2.5/forecast?id=4508722&APPID=00b1eab8137a0b1d81025d667dbb2f17&units=imperial'
	h = httplib2.Http()

	raw = h.request(url,'GET')[1]

	results = json.loads(raw.decode())

	weather_main = results['list'][0]['weather'][0]['main']
	weather_desc = results['list'][0]['weather'][0]['description']
	weather_temp = results['list'][0]['main']['temp']
	weather_temp_max = results['list'][0]['main']['temp_max']
	weather_temp_min = results['list'][0]['main']['temp_min']

	weather_data = (weather_main, weather_desc, weather_temp, weather_temp_max, weather_temp_min)
	print("Weather API Updated")
	return weather_data

def getInjuryRates():
	db, cursor = connect()

	incident_query = """
    		SELECT case_num,
    				to_char(date_time, 'FMMonth FMDD, YYYY'),
	    			to_char(date_time, 'HH24:MI'), 
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

	total_i = 0
	total_fa = 0
	total_ri = 0
	total_rd = 0
	total_lti = 0
	for r in results:
		if r[3] == 'FA':
			total_fa = total_fa + 1
			total_i = total_i + 1
		if r[3] == 'RI':
			total_ri = total_ri + 1
			total_i = total_i + 1
		if r[3] == 'RD':
			total_rd = total_rd + 1
			total_i = total_i + 1
		if r[3] == 'LTI':
			total_lti = total_lti + 1
			total_i = total_i + 1
	total_rir = total_ri+total_rd+total_lti

	hours_query = """
			SELECT sum(hours) as num
				FROM manhours
				WHERE year = 2017
				"""
	cursor.execute(hours_query)
	hour_results = cursor.fetchone()
	manhours = hour_results[0]
	fair = round(float(total_fa*200000)/float(manhours), 2)
	rir = round(float(total_rir*200000)/float(manhours), 2)
	lti = round(float(total_lti*200000)/float(manhours), 2)
	ori = round(float(total_ri*200000)/float(manhours), 2)
	tir = round(float(total_i*200000)/float(manhours), 2)

	injury_rate = (fair, rir, lti, ori, tir)
	db.close()

	return injury_rate
