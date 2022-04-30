from flask import Flask, render_template, g, request, redirect
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
    return render_template("home.html", active='home')


current_question = 0
@app.route("/question")
def question():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"
    cursor.execute(query)
    information = cursor.fetchall()
    global current_question
    current_question = 1
    return render_template("question.html", information=information, active='question', current_question = current_question)


@app.route("/user_answer", methods=['GET', 'POST'])
def user_answer():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"
    cursor.execute(query)
    information = cursor.fetchall()
    
    global current_question

    try:
        answer = request.form["answer"]
    except:
        answer = None
    cursor = get_db().cursor()
    query = "UPDATE question SET user_choice = ? WHERE picture_file = ?"
    print("information[current_question][0]")
    cursor.execute(query,(answer, information[current_question-1][0]))
    get_db().commit()
    
    current_question = current_question + 1
    return render_template("question.html", information=information, active='question', current_question = current_question)


if __name__ == "__main__":
    app.run(debug=True)
