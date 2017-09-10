# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
user = 'safety'
password ='safety'
database = 'safety_v2'
url = 'postgresql://{}:{}@{}:{}/{}'
SQLALCHEMY_DATABASE_URI = url.format(user, password, host, port, db)
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "super secret key"

# Secret key for signing cookies
SECRET_KEY = "super secret key"