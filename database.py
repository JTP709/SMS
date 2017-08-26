#!/usr/bin/python
 
import psycopg2
from config import config
  
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TYPE type AS ENUM (
        	'Injury',
        	'PIT Incident',
        	'Near Miss',
        	'HAZMAT'
        )
        """,
        """
        CREATE TYPE category AS ENUM (
        	'Unsafe Act',
        	'Unsafe Behavior',
        	'Unsafe Condition'
        )
        """,
        """
        CREATE TYPE audit_type AS ENUM (
        	'Behavior',
        	'Area Organization',
        	'HAZWASTE'
        )
        """,
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            picture TEXT,
            position TEXT
        )
        """,
        """
        CREATE TABLE incident (
	        case_num SERIAL PRIMARY KEY,
            date_time TIMESTAMP default NULL,
	        incident_type type NOT NULL,
	        incident_cat category NOT NULL,
	        injury BOOLEAN NOT NULL,
	        property_damage BOOLEAN NOT NULL,
	        description TEXT,
	        root_cause TEXT,
            user_id INTEGER REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE audit (
	        id SERIAL PRIMARY KEY,
            date_time TIMESTAMP default NULL,
	        type audit_type NOT NULL,
            que_1 TEXT NOT NULL,
            que_2 TEXT,
            que_3 TEXT,
            ans_1 BOOLEAN,
            ans_2 BOOLEAN,
            ans_3 BOOLEAN,
            user_id INTEGER REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE action_items (
            id SERIAL PRIMARY KEY,
            date_time TIMESTAMP default NULL,
            case_id INTEGER REFERENCES incident(case_num),
            audit_id INTEGER REFERENCES audit(id),
            finding TEXT,
            corrective_action TEXT,
            due_date TIMESTAMP default NULL,
            open_close BOOLEAN,
            user_id INTEGER REFERENCES users(id)
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect("dbname = safety")
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    print("Tables have been created!")

if __name__ == '__main__':
    create_tables()