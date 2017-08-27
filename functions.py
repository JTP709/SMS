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

