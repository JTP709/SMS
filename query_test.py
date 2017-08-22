import psycopg2

def connect(database_name="safety"):
    """Connects to database"""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print ("<error message>")

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
	return results
	db.close()

if __name__=="__main__":
	dashboard = dashboard()
	#print(dashboard)
	for i in range(len(dashboard)):
		print(dashboard[i][1])
		
