from sqlalchemy import create_engine

def connect(user='safety', password='safety',db='safety_v2', host='localhost', port=5432):
	"""Returns a connection and a metadata object"""
	url = 'postgresql://{}:{}@{}:{}/{}'
	url = url.format(user, password,host, port, db)
	con = create_engine(url, client_encoding ='utf8')
	return con