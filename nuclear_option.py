import psycopg2
from config import config
from functions import connect

def nuclearOption():
	db, cursor = connect()
	
	nuke = """
			DROP TABLE incident CASCADE;
			DROP TABLE audit CASCADE;
			DROP TABLE action_items CASCADE;
			DROP TABLE manhours CASCADE;
			DROP TABLE users CASCADE;
			DROP TYPE type;
			DROP TYPE category;
			DROP TYPE audit_type;
			"""
	cursor.execute(nuke)
	db.commit()
	db.close()
	print("Nuked!")

nuclearOption()