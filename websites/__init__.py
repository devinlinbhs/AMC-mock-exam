# Making the websites folder a python package 
# We can import the things in this folder into other files
# Once the website file is imported, whatever is inside __init__.py will automatically run
from flask import Flask

app = Flask(__name__)
# __name__ represents the name of the application package and flask identifies resources like templates, static assets and the instance folder.


import sqlite3
from flask import g

DATABASE = 'AMC.db'
# Database name

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
# Connect to database? How?

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
# How does it close the database?
        

def create_app():
    app.config['SECRET_KEY'] = 'asdfghjkl'
    from .views import views
    from .auth import auth
    # import the contents from the python files so it can be used in the initialize file?
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    # Blueprint allowing routing to be used in more than 1 python files to re-arrange the routes
    
    return app