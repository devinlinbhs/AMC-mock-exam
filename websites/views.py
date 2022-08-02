from websites import get_db
from flask import Blueprint, redirect, request, render_template, session, url_for 
import random

views = Blueprint('views', __name__)


@views.route("/")
def home():
    try:
        if session['login']:
            return render_template("home.html", active='home')
            # if user logged in, go to home page
        else:
            return redirect (url_for('auth.login'))
        # else go to login page
    except KeyError:
        return redirect (url_for('auth.login'))
        


@views.route("/setting_exam")
def setting_exam():
    if session['login']:
        return render_template("setting_exam.html", active='setting_exam')
        # ensuring user is logged in
    else:
        return redirect (url_for('auth.login'))


views.secret_key = "asdfghjkl"
#setting up the secret key for session





# Question page
# For the users to answer muti-choice questions(Will be used for Radom Quizes and Past Exam Practices at some point)
@views.route("/question", methods = ["GET","POST"])
def question():
    if session['login']:
        year = request.form['year']
        difficulty = request.form["difficulty"]
        # Get the values from the drop down menu
        
        past_paper_id = 0
        if difficulty == "senior":
            past_paper_id += 10
        elif difficulty == "intermediate":
            past_paper_id += 5
        else:
            past_paper_id += 0
            
        if year == "2020":
            past_paper_id += 5
        elif year == "2019":
            past_paper_id += 4
        elif year == "2018":
            past_paper_id += 3
        elif year == "2017":
            past_paper_id += 2
        elif year == "2016":
            past_paper_id += 1
        # The corresponding past_paper_id value in the database
        
        session["past_paper_id"] = str(past_paper_id)
        
        session['file_location'] = year +'_'+difficulty
        # Create a string which is exactly the file location

        cursor = get_db().cursor()
        query = "SELECT picture_file FROM question WHERE past_paper_id = ?"
        # Create a cursor to deliver query in the database

        cursor.execute(query,(past_paper_id,))
        session['information'] = cursor.fetchall()
        # Get all the picture files in a tuple
        
        return render_template("question.html", active='setting_exam')
        # Lead to question.html, pass the picture_files to the website with the current question, and the current active website
    else:
        return redirect (url_for('auth.login'))

# Upload the answer for each question that the users submitted
@views.route("/upload_user_answer", methods=['GET', 'POST'])
def upload_user_answer():
    if session['login']:
        cursor = get_db().cursor()
        
        query = "SELECT picture_file, answer FROM question WHERE past_paper_id = ?"
        cursor.execute(query,(session['past_paper_id'],))
        session['information'] = cursor.fetchall()
        # Get picture file and the model answer of all question in that paper
        
        
        query = "INSERT INTO completed_paper (user_id, past_paper_id,score) VALUES (?,?,?);"
        cursor.execute(query,(session['user_id'],session['past_paper_id'],"new_paper"))
        # session['user_id'] is defined when the user is logged in and stored as his id
        
        get_db().commit()
        # Create a completed paper
        
        query = "SELECT id FROM completed_paper WHERE score = 'new_paper'"
        cursor.execute(query)
        completed_paper_id = cursor.fetchall()
        # Select the id just created
        
        query = "UPDATE question SET user_choice = ? WHERE picture_file = ?"
        # Update the user's answer query
        query_for_storing_answer = "INSERT INTO stored_answer (completed_paper_id, picture_file, question_number, answer, user_choice) VALUES (?,?,?,?,?);"
        # Store the user's answer query
        
        
        for i in range(25):
            current_question = i+1
            # create a counting variable

            try:
                answer = request.form["answer" + str(current_question)]
    # Now bring the value of the "answer1" or "answer2" etc from the question.html, the user's choice for the question to the python file

            except:
                answer = ''
                # If there is no answer then there will be error, thus do this route

            cursor.execute(query, (answer, session['information'][current_question-1][0]))
            cursor.execute(query_for_storing_answer, (completed_paper_id[0][0], session['information'][current_question-1][0], current_question, session['information'][current_question-1][1], answer))
            # Update the data into the database
        get_db().commit()

        cursor = get_db().cursor()
        query = "SELECT answer, user_choice FROM question WHERE past_paper_id = ?"


        cursor.execute(query,(session['past_paper_id'],))
        session['marking_scheme'] = cursor.fetchall()
        # To get the user's answers VS the model answers in the database

        score = 0
        # Create a new variable

        for count in range(25):
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
            
        query = "UPDATE completed_paper SET score = ? WHERE score = 'new_paper'"
        cursor.execute(query,(score,))
        get_db().commit()
        # Record the score about this completed paper

        return render_template("score.html", run='', score=score)
    else:
        return redirect (url_for('auth.login'))








@views.route("/setting_quiz")
def setting_quiz():
    if session['login']:
        return render_template("setting_quiz.html", active='setting_quiz')
    else:
        return redirect (url_for('auth.login'))

@views.route("/quiz", methods = ["GET","POST"])
def quiz():
    if session['login']:
        set = request.form["set"]
        # set will determine what type of quiz we are doing
        
        difficulty = request.form["difficulty"]
        # difficulty will determine how hard the overall paper is


        session['file_location_set'] = []
        # This will be passed to the website, which helps the "url_for" to find the picture file position
        
        session['marking_scheme'] = []
        # This ensures the marking_scheme of the mixed list is passed to the marking route for 
        # quiz without messing up the correct answer for the random questions
        
        session['question_set'] = []
        # Create a list to store the name of the random questions' images
        
        past_paper_id = 0
        # To create a past_paper_id calculation method
        
        if difficulty == "senior":
            past_paper_id += 10
        elif difficulty == "intermediate":
            past_paper_id += 5
        else:
            past_paper_id += 0
        
        
        cursor = get_db().cursor()
        query = "SELECT picture_file, answer FROM question WHERE past_paper_id = ? AND question_number = ?"
        # This will be the query we use every time in the for loop
        # Get the image name and also the correct answer from the database
        
        
        if set == "set1":
            session['constant'] = 1
            run = 10
            # session['Constant'] will be add to the {i} to get the question number we supposed to be on
            # "set" determine how many times we run the for loop
            
        elif set == "set2":
            session['constant'] = 11
            run = 10
            
        else:
            session['constant'] = 21
            run = 5
            
        for i in range (run):
            question_number = i + session['constant']
            year = random.randint(2016, 2020)
            
            past_paper_id_value = str(past_paper_id + year - 2015)
            # This is the actual past_paper_id we put into the query to select the corresponding image
            
            cursor.execute(query,(past_paper_id_value, question_number))
            random_question = cursor.fetchall()

            session['question_set'].append(random_question[0][0])
            # Store the name of the image into the list, so we can recall the 
            # names/locations of the images in HTML
            
            session['marking_scheme'].append(random_question[0][1])
            # Store the correct answer and pass onto the marking route
            
            session['file_location'] = str(year)+'_'+difficulty
            session['file_location_set'].append(session['file_location'])
            # Adding the file location of each image correspondingly to recall them in the HTML

            session['run'] = run
        return render_template("quiz.html", run=run, active = "setting_quiz")
    else:
        return redirect (url_for('auth.login'))


@views.route("/upload_user_answer_quiz", methods=['GET', 'POST'])
def upload_user_answer_quiz():
    if session['login']:
        session['answer_set'] = []
        run = session['run']
        for i in range(run):
            current_question = i+1
            # create a counting variable

            try:
                session['answer_set'].append(request.form["answer" + str(current_question)])
    # Now bring the value of the "answer1" or "answer2" etc from the question.html, the user's choice for the question to the python file

            except:
                session['answer_set'].append('')
                # If there is no answer then there will be error, thus do this route

        score = 0
        # Create a new variable
        
        if run == 5:
            type = "quiz_5"
        else:
            type = "quiz_10"
        # This tells the HTML what is the mark actually out of
        
        for count in range(run):
            if session['marking_scheme'][count] == session['answer_set'][count]:
                score += 1

        return render_template("score.html", run=run, score=score, type = type)
    else:
        return redirect (url_for('auth.login'))
    
    
    
    
@views.route("/filter_completed_paper", methods = ["GET","POST"])
def filter_completed_paper():
    session['completed'] = []
    session['highest_score'] = []
    session['name_of_paper_list'] = []
    # Completed will store the name of the paper completed
    # Highest_score will store the highest store of that paper completed
    # Name of past paper list store the year and difficulty of those papers
    
    cursor = get_db().cursor()
    query = "SELECT DISTINCT past_paper_id FROM completed_paper WHERE user_id = ? ORDER BY past_paper_id DESC"
    cursor.execute(query,(session['user_id'],))
    # session['user_id'] is defined when the user is logged in and stored as his id
    session['amount_of_different_paper'] = cursor.fetchall()
    # Select the different paper done by the CURRENT user, with the past paper id
    
    
    for i in range(len(session['amount_of_different_paper'])):
        # Run the loop the amount of time that the amount of different past paper the user done
        query = "SELECT year, difficulty FROM past_paper WHERE id = ?"
        cursor.execute(query,(session['amount_of_different_paper'][i][0],))
        # amount_of_past_paper[i][0] correspond with the 'past_paper_id' in completed paper table thus the 'id' in past paper table
        
        name_of_paper = cursor.fetchall()
        session['name_of_paper_list'].append(name_of_paper)
        
        query = "SELECT COUNT(past_paper_id) FROM completed_paper WHERE past_paper_id = ? AND user_id = ?"
        cursor.execute(query,(session['amount_of_different_paper'][i][0], session['user_id']))
        number_of_time_completed = cursor.fetchall()[0][0]
        # number_of_time_completed = the number of time completed on that paper
        
        actual_paper = f"AMC {session['name_of_paper_list'][i][0][0]} {session['name_of_paper_list'][i][0][1]} (completed {number_of_time_completed} times)"
        # session['name_of_paper_list'][i][0][0] = year, session['name_of_paper_list'][i][0][1] = difficulty 
        
        
        session['completed'].append(actual_paper)
        # Add the information into the list and will be used in the filter page to display
        
        
        
        
        query = "SELECT MAX(score) FROM completed_paper WHERE past_paper_id = ? AND user_id = ? ORDER BY past_paper_id DESC"
        cursor.execute(query,(session['amount_of_different_paper'][i][0], session['user_id']))
        # Select only the top score in -->  session['amount_of_different_paper'][i][0] = past_paper_id
        # Basically the top score in each past paper completed
        
        # Thus if the user completed past_paper_id:15 for 3 times, we only show the highest score 
        # session['user_id'] is defined when the user is logged in and stored as his id
        highest_score = cursor.fetchall()[0][0]
        # The highest score that the user completed 
        
        session['highest_score'].append(highest_score)
        # Add them all into a list and display them in front of the user in filter_completed_paper.html
        
    return render_template("filter_completed_paper.html", number_of_completed = len(session['completed']), 
        active="result")
    
@views.route("/past_result/<int:table_number>", methods = ["GET","POST"])
def past_result(table_number):
    cursor = get_db().cursor()
    # session['name_of_paper_list'][i][0][0] = year, session['name_of_paper_list'][i][0][1] = difficulty
    # session['highest_score'][i] = highest score of that 'year','difficulty','user'
    # session['amount_of_different_paper'][i][0] = past_paper_id
    
    session['file_location'] = str(session['name_of_paper_list'][table_number][0][0]) +'_'+session['name_of_paper_list'][table_number][0][1]
    # File location defined by using the link that the user has clicked in the filter page
    
    query = "SELECT picture_file FROM question WHERE past_paper_id = ?"
    cursor.execute(query,(session['amount_of_different_paper'][table_number][0],))
    # recall session['amount_of_different_paper'][i][0] = past_paper_id
    session['information'] = cursor.fetchall()
    # Get the images of the questions for the specific question
    
    query = "SELECT id, score FROM completed_paper WHERE user_id = ? AND past_paper_id = ? AND score = ?"
    cursor.execute(query,(session['user_id'], session['amount_of_different_paper'][table_number][0],
                    session['highest_score'][table_number]))
    session['completed_paper_id'] = cursor.fetchall()
    # session['completed_paper_id'][0][0] = 'id' of the specific 'user' + 'completed_paper' + 'highest score'
    # session['completed_paper_id'][0][1] = 'score' of that paper
    
    query = "SELECT answer, user_choice FROM stored_answer WHERE completed_paper_id = ?"
    cursor.execute(query,(session['completed_paper_id'][0][0],))
    session['marking_scheme'] = cursor.fetchall()
    # Get the user answer about the highest score paper
    
    
    return render_template("past_result.html",active="result")
    
    
@views.route("/completed_paper", methods = ["GET","POST"])
def completed_paper():
    return render_template("completed_paper.html")