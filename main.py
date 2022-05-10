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


# Create a homepage (tempoaray right now)
@app.route("/")
def home():

    return render_template("home.html", active='home')


@app.route("/setting_exam")
def setting_exam():
    return render_template("setting_exam.html")


# Question page
# For the users to answer muti-choice questions(Will be used for Radom Quizes and Past Exam Practices at some point)
@app.route("/question", methods = ["GET","POST"])
def question():
    year = request.form["year"] # Problem is here
    difficulty = request.form["difficulty"]
    if difficulty == "senior":
        foreign_id = "3"
    elif difficulty == "intermediate":
        foreign_id = "2"
    else:
        foreign_id = "1"
    file_location = year+'_'+difficulty
    print(file_location)

    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question WHERE year = ? AND difficulty = ?"
    # Create a cursor to deliver query in the database

    cursor.execute(query,(year,foreign_id))
    information = cursor.fetchall()
    print(information)
    # Get all the picture files in a tuple
    # Need a better way to get the name of the picture files when there is much more data in the database
    

    return render_template("question.html", information=information, active='setting_exam', file_location = file_location)
    # Lead to question.html, pass the picture_files to the website with the current question, and the current active website


# Upload the answer for each question that the users submitted
@app.route("/upload_user_answer", methods=['GET', 'POST'])
def upload_user_answer():

    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question"

    cursor.execute(query)
    information = cursor.fetchall()

    query = "UPDATE question SET user_choice = ? WHERE picture_file = ?"
    # Update the user's answer query

    for i in range(30):
        current_question = i+1
        # create a counting variable

        try:
            answer = request.form["answer" + str(current_question)]
# Now bring the value of the "answer1" or "answer2" etc from the question.html, the user's choice for the question to the python file

        except:
            answer = ''
            # If there is no answer then there will be error, thus do this route

        cursor.execute(query, (answer, information[current_question-1][0]))
        # Update the data into the database

    get_db().commit()
    # Execute then save it

    return redirect("check_answer")
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
