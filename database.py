#!/usr/bin/python
 
import psycopg2
from config import config
  
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TYPE type AS ENUM(
        	'Injury',
        	'PIT Incident',
        	'Near Miss',
        	'HAZMAT'
        )
        """,
        """
        CREATE TYPE category AS ENUM(
        	'Unsafe Act
        	'Unsafe Behavior',
        	'Unsafe Condition'
        )
        """,
        """
        CREATE TYPE audit_type AS ENUM(
        	'Behavior',
        	'Area Organization',
        	'Regulatory Compliance'
        )
        """,
        """
        CREATE TABLE incident (
	        case_num SERIAL PRIMARY KEY,
	        incident_type type NOT NULL,
	        incident_cat category NOT NULL,
	        injury BOOLEAN NOT NULL,
	        property_damage BOOLEAN NOT NULL,
	        description TEXT,
	        root_cause TEXT
        )
        """,
        """
        CREATE TABLE audit (
	        id SERIAL PRIMARY KEY,
	        type audit_type NOT NULL,
            que_1 TEXT(500) NOT NULL,
            que_2 TEXT(500),
            que_3 TEXT(500),
            ans_1 TEXT(1000),
            ans_2 TEXT(1000),
            ans_3 TEXT(1000)
        )
        """,
        """
        CREATE TABLE action_items (
            id SERIAL PRIMARY KEY,
            case_id INTEGER REFERENCES incident(case_num),
            audit_id INTEGER REFERENCES audit(id),
            finding TEXT,
            corrective_action TEXT
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
 
 
if __name__ == '__main__':
    create_tables()