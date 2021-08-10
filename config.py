import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database



#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/fyyur'
# Connect to the database

class DatabaseURI:

    # Just change the names of your database and crendtials and all to connect to your local system
    DATABASE_NAME = "fyyur"
    username = 'postgres'
    password = '1234'
    url = 'localhost:5432'
    dialects = 'postgresql'
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}/{}".format(
        dialects,username, password, url, DATABASE_NAME)
