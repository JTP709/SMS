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
