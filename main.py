from flask import Flask, render_template, g, request
import sqlite3

#Basic set up

#Database name
DATABASE = "AMC.db"


app = Flask(__name__)

#Open connection to database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#Close connection from database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#Create a homepage (tempoaray right now)
@app.route("/")
def home():
    return render_template("home.html", active='home')

#Create a global variable that counts which question the user is currently on
current_question = 0

#Question page
#For the users to answer muti-choice questions(Will be used for Radom Quizes and Past Exam Practices at some point)
@app.route("/question")
def question():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"
    #Create a cursor to deliver query in the database
    
    cursor.execute(query)
    information = cursor.fetchall()
    #Get all the picture files in a tuple
    ### Need a better way to get the name of the picture files when there is much more data in the database
        
    global current_question
    current_question = 1
    #Bring the global variable to local and set it to the first question
    
    return render_template("question.html", information=information, active='question', current_question = current_question)
    #Lead to question.html, pass the picture_files to the website with the current question, and the current active website

@app.route("/user_answer", methods=['GET', 'POST'])
def user_answer():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"
    #Create a cursor to deliver query in the database
    
    cursor.execute(query)
    information = cursor.fetchall()
    #Get all the picture files in a tuple
    
    
    try:
        answer = request.form["answer"]
    except:
        answer = None
    # Now bring the value of the "answer" from the question.html, the user's answer to the question to the python file

    global current_question    
    cursor = get_db().cursor()
    query = "UPDATE question SET user_choice = ? WHERE picture_file = ?"
    print("information[current_question][0]")
    # Update the user's answer query
    
    cursor.execute(query,(answer, information[current_question-1][0]))
    get_db().commit()
    # Execute then save it
    
    current_question = current_question + 1
    return render_template("question.html", information=information, active='question', current_question = current_question)
    # Move on to next question in question.html, pass down the same file name, active website question.html

if __name__ == "__main__":
    app.run(debug=True)
    # Real time update to the web application