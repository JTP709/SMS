import psycopg2

def connect(database_name="safety"):
    """Connects to database"""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print ("<error message>")

def query_1():
	db, cursor = connect()
	audit_query = """
    		SELECT count(*) as num
    			FROM audit
    			WHERE ans_1 = FALSE OR
    				ans_2 = FALSE OR
    				ans_3 = FALSE
            """
	cursor.execute(audit_query)
	audit_results = cursor.fetchone()
	return audit_results
	db.close()

def query_2():
	db, cursor = connect()
	audit_query_t = """
			SELECT count(*) as num
				FROM audit
			"""

	cursor.execute(audit_query_t)
	audit_totals = cursor.fetchone()

	return audit_totals
	db.close()

if __name__=="__main__":
	query_1 = query_1()
	query_2 = query_2()
	print(int(query_1[0]))
	print(int(query_2[0]))
	health = round(float(float(query_1[0])/float(query_2[0]))*100,2)
	print(health)
	#for i in range(len(dashboard)):
	#	print(dashboard[i])		
