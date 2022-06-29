# Making the websites folder a python package 
# We can import the things in this folder into other files
# Once the website file is imported, whatever is inside __init__.py will automatically run
from flask import Flask

app = Flask(__name__)

def create_app():
    
    app.config['SECRET_KEY'] = 'asdfghjkl'
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    
    return app


