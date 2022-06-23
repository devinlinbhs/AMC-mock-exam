from flask import Flask, render_template, g, request, redirect, session
import sqlite3
import random

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



@app.route("/")
def home():
    return render_template("home.html", active='home')


@app.route("/setting_exam")
def setting_exam():
    return render_template("setting_exam.html")


app.secret_key = "asdfghjkl"






# Question page
# For the users to answer muti-choice questions(Will be used for Radom Quizes and Past Exam Practices at some point)
@app.route("/question", methods = ["GET","POST"])
def question():
    
    session['year'] = request.form['year']
    difficulty = request.form["difficulty"]
    # Get the values from the drop down menu
    
    if difficulty == "senior":
        session['foreign_id'] = "3"
    elif difficulty == "intermediate":
        session['foreign_id'] = "2"
    else:
        session['foreign_id'] = "1"
    # The corresponding foreignkey value in the database
    
    file_location = session['year']+'_'+difficulty
    # Create a string which is exactly the file location

    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question WHERE year = ? AND difficulty = ?"
    # Create a cursor to deliver query in the database

    cursor.execute(query,(session['year'],session['foreign_id']))
    information = cursor.fetchall()
    # Get all the picture files in a tuple
    
    
    return render_template("question.html", information=information, active='setting_exam', file_location = file_location)
    # Lead to question.html, pass the picture_files to the website with the current question, and the current active website


# Upload the answer for each question that the users submitted
@app.route("/upload_user_answer", methods=['GET', 'POST'])
def upload_user_answer():
    
    cursor = get_db().cursor()
    query = "SELECT picture_file FROM question WHERE year = ? AND difficulty = ?"
    
    cursor.execute(query,(session['year'], session['foreign_id']))
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

    cursor = get_db().cursor()
    query = "SELECT answer, user_choice FROM question WHERE year = ? AND difficulty = ?"


    cursor.execute(query,(session['year'], session['foreign_id']))
    session['marking_scheme'] = cursor.fetchall()
    # To get the user's answers VS the model answers in the database

    score = 0
    # Create a new variable

    for count in range(30):
        question_number = count + 1
        # The real question number is always 'count' + 1

        if 1 <= question_number <= 10:
            if session['marking_scheme'][count][0] == session['marking_scheme'][count][1]:
                score += 3
        # Question 1 ~ 10 worth 3 points each

        elif 11 <= question_number <= 20:
            if session['marking_scheme'][count][0] == session['marking_scheme'][count][1]:
                score += 4
        # Question 11 ~ 20 worth 4 points each

        else:
            if session['marking_scheme'][count][0] == session['marking_scheme'][count][1]:
                score += 5
        # Qquestion 21 ~ 25 worth 5 points each


    return render_template("score.html", score=score)








@app.route("/setting_quiz")
def setting_quiz():
    return render_template("setting_quiz.html")


@app.route("/quiz", methods = ["GET","POST"])
def quiz():
    
    set = request.form["set"]
    difficulty = request.form["difficulty"]

    file_location_set = []
    
    session['marking_scheme'] = []
    session['year_set'] = []
    session['question_set'] = []
    
    if difficulty == "senior":
        session['foreign_id'] = "3"
    elif difficulty == "intermediate":
        session['foreign_id'] = "2"
    else:
        session['foreign_id'] = "1"
    
    
    cursor = get_db().cursor()
    query = "SELECT picture_file, answer FROM question WHERE year = ? AND difficulty = ? AND question_number = ?"
    
        
    
    if set == "set1":
        constant = 1
        session['run'] = 10
        # Constant will be add to the {i} to get the question number we supposed to be on
        # session['year_set'] determine how many times we run the for loop
        
    elif set == "set2":
        constant = 11
        session['run'] = 10
        
    else:
        constant = 21
        session['run'] = 5
        
    for i in range (session['run']):
        question_number = i + constant
        year = random.randint(2016, 2020)
        session['year_set'].append(year)
        
        cursor.execute(query,(year,session['foreign_id'], question_number))
        random_question = cursor.fetchall()

        session['question_set'].append(random_question[0][0])
        session['marking_scheme'].append(random_question[0][1])
        
        file_location = str(year)+'_'+difficulty
        file_location_set.append(file_location)

    return render_template("quiz.html", question_set = session['question_set'], file_location_set = file_location_set,
                            run = session['run'], constant = constant, active = "setting_quiz")


@app.route("/upload_user_answer_quiz", methods=['GET', 'POST'])
def upload_user_answer_quiz():
    
    answer_set = []
    for i in range(session['run']):
        current_question = i+1
        # create a counting variable

        try:
            answer_set.append(request.form["answer" + str(current_question)])
# Now bring the value of the "answer1" or "answer2" etc from the question.html, the user's choice for the question to the python file

        except:
            answer_set.append('')
            # If there is no answer then there will be error, thus do this route

    score = 0
    # Create a new variable
    if session['run'] == 5:
        type = "quiz_5"
    else:
        type = "quiz_10"
    
    for count in range(session['run']):
        if session['marking_scheme'][count] == answer_set[count]:
            score += 1

    return render_template("score.html", score=score, type = type)




if __name__ == "__main__":
    app.run(debug=True)
    # Real time update to the web application
