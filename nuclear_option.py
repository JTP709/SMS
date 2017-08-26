import psycopg2
from config import config

def nuclearOption():
	params = config()
	conn = psycopg2.connect("dbname = safety")
	cur = conn.cursor()
	nuke = """
			DROP TABLE incident CASCADE;
			DROP TABLE audit CASCADE;
			DROP TABLE action_itmes CASCADE;
			DROP TYPE type;
			DROP TYPE category;
			DROP TYPE audit_type;
			"""
	cur.execute(nuke)
	db.commit()
	db.close()

nuclearOption()