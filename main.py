from flask import Flask, render_template, g
import sqlite3

DATABASE = "AMC.db"


app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"
    cursor.execute(query)
    information = cursor.fetchall()
    return render_template("home.html", information = information) 


if __name__ == "__main__":
    app.run(debug=True)
