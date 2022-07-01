from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from websites import get_db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if session['login'] == False:
        if request.method == 'POST':
            account_name = request.form.get('account_name')
            password = request.form.get('password')
            cursor = get_db().cursor()
            query = "SELECT * FROM user WHERE account_name = ?;"
            cursor.execute(query, (account_name,))
            user = cursor.fetchall()
            if user:
                if check_password_hash(user[0][2], password):
                    flash('Logged in successfully!', category='success')
                    session['login'] = True
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Account Name doesn\'t exist, try again.', category='error')
            
        return render_template('login.html')
    else:
        return redirect(url_for('views.home'))

@auth.route('/logout')
def logout():
    session['login'] = False
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if session['login'] == False:
        if request.method == 'POST':
            account_name = request.form.get('account_name')
            user_name = request.form.get('user_name')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            
            cursor = get_db().cursor()
            query = "SELECT * FROM user WHERE account_name = ?;"
            
            cursor.execute(query, (account_name,))
            user = cursor.fetchall()
            
            if user:
                flash('Account Name already exist, please use a different Account Name', category='error')
            elif len(account_name) < 6:
                flash('Account name must be at least 6 characters.', category='error')
            elif len(user_name)<2:
                flash('Account name must be at least 2 characters.', category='error')
            elif password1 != password2:
                flash('Password don\'t match.', category='error')
            elif len(password1)<8:
                flash('Password must be at least 8 characters.', category='error')
            else:
                session['account_name'] = account_name
                session['user_name'] = user_name
                session['password1'] = password1
                flash('Account created!', category='success')
                #Add user to database
                return redirect(url_for('auth.add'))
                
        return render_template('sign_up.html')
    else:
        return redirect(url_for('views.home'))

@auth.route("/add", methods=["GET", "POST"])
# By the time you click the "submit button", "Comfirm Add Item", the action of the form will lead to this route
# When you hit the "submit", the "text input", item_name and item_description
# will have their value exactly as the user input
def add():
    cursor = get_db().cursor()
    query = "INSERT INTO user (account_name, password, user_name) VALUES (?,?,?);"
    # And in this route, connect to the database

    cursor.execute(query, (session['account_name'], generate_password_hash(session['password1'], method='sha256'),session['user_name'],))
    
    get_db().commit()
    session['login'] = True
    return redirect(url_for('views.home'))
    # Back to the main page