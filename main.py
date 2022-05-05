from flask import Flask, render_template, g, request, redirect
import sqlite3

# Basic set up

# Database name
DATABASE = "AMC.db"


app = Flask(__name__)


# Open connection to database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db



# Close connection from database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Create a global variable that counts which question the user is currently on


# Create a homepage (tempoaray right now)
@app.route("/")
def home():
    # Reset the question number to 0 so users can start from the begining next time
    # Eliminated bugs that started from E.g. Q23

    cursor = get_db().cursor()
    query = "UPDATE question SET user_choice = ?"
    # Clear the previous answers for the exam
    # Eliminated bugs that you get what you scored last time if you end the exam from Q1

    cursor.execute(query, ('',))
    get_db().commit()

    return render_template("home.html", active='home')


# Question page
# For the users to answer muti-choice questions(Will be used for Radom Quizes and Past Exam Practices at some point)
@app.route("/question")
def question():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"
    # Create a cursor to deliver query in the database

    cursor.execute(query)
    information = cursor.fetchall()
    # Get all the picture files in a tuple
    # Need a better way to get the name of the picture files when there is much more data in the database

    # Bring the global variable to local and set it to the first question

    return render_template("question.html", information=information, active='question')
    # Lead to question.html, pass the picture_files to the website with the current question, and the current active website


# Upload the answer for each question that the users submitted
@app.route("/upload_user_answer", methods=['GET', 'POST'])
def upload_user_answer():
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"

    cursor.execute(query)
    information = cursor.fetchall()
    

    try:
        answer = request.form["answer"]
        current_question = request.form["group_id"]
        current_question = int(current_question)
    except:
        answer = None
    # Now bring the value of the "answer" from the question.html, the user's answer to the question to the python file

    
    cursor = get_db().cursor()
    query = "UPDATE question SET user_choice = ? WHERE picture_file = ?"
    # Update the user's answer query

    cursor.execute(query, (answer, information[current_question-1][0]))
    get_db().commit()
    # Execute then save it

    return redirect("question")
    # Move on to next question in question.html, pass down the same file name, active website question.html


@app.route("/check_answer")
def check_answer():
    cursor = get_db().cursor()
    query = "SELECT answer, user_choice FROM question"


    cursor.execute(query)
    marking_scheme = cursor.fetchall()
    # To get the user's answers VS the model answers in the database

    score = 0
    # Create a new variable
    
    for count in range(30):
        question_number = count + 1
        # The real question number is always 'count' + 1
        
        if 1 <= question_number <= 10:
            if marking_scheme[count][0] == marking_scheme[count][1]:
                score += 3
        # Question 1 ~ 10 worth 3 points each        
                
        elif 11 <= question_number <= 20:
            if marking_scheme[count][0] == marking_scheme[count][1]:
                score += 4
        # Question 11 ~ 20 worth 4 points each         
                
        elif 21 <= question_number <= 25:
            if marking_scheme[count][0] == marking_scheme[count][1]:
                score += 5
        # Qquestion 21 ~ 25 worth 4 points each             
                
        else:
            if marking_scheme[count][0] == marking_scheme[count][1]:
                score += question_number - 20
        # Q26 : 6 points; Q27 : 7 points; Q28 : 8 points; Q29 : 9 points; Q30 : 10 points, 

    return render_template("score.html", score=score)


if __name__ == "__main__":
    app.run(debug=True)
    # Real time update to the web application
