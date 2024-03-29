from flask import Blueprint, render_template, request, redirect, session, url_for
from websites import get_db
from werkzeug.security import generate_password_hash, check_password_hash
# import functions


auth = Blueprint('auth', __name__)
# Understand Blueprint later


@auth.route('/login', methods=['POST', 'GET'])
def login():
    try:
        if session['login'] == False:
            session['login_error']= None
            session['sign_up_error']= None
        # So only can go to this route if user isn't logged in
        
            if request.method == 'POST':
                # Only when user is submitting data
                
                
                account_name = request.form.get('account_name_1')
                password = request.form.get('password')
                # Get users' input
                
                cursor = get_db().cursor()
                query = "SELECT * FROM user WHERE account_name = ?;"
                # Find the information of the user with that account_name in the database
                
                cursor.execute(query, (account_name,))
                user = cursor.fetchall()
                # Get all the information of that user
                
                if user:
                # If the information is not empty, i.e. user exists
                
                    if check_password_hash(user[0][2], password):
                    # If the password entered then hashed is equal to the hashed password stored, 
                    # then the password is correct

                        
                        session['login'] = True
                        # Showing user is logged in in the backend

                        session['user_id'] = user[0][0]
                        session['user_name'] = user[0][3]
                        
                        return redirect(url_for('views.home'))
                        # Go to home page
                    else:
                        session['login_error']='Incorrect password, try again.'
                        # Hashed passwords are not the same, give error messages
                else:
                    session['login_error']='Account Name doesn\'t exist, try again.'
                    # If there is no information, then there is no such a user
                
            return render_template('login.html')
            # After all, user didn't logged in, so display login.html
        else:
            return redirect(url_for('views.home'))
            # If user already logged in, they should be in home page
    except KeyError:
        return redirect (url_for('auth.logout'))

@auth.route('/logout')
def logout():
    session['login'] = False
    # Now the user is logged out
    return render_template("intro.html")
    # Go to log in page

@auth.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if session['login'] == False:
        session['login_error']= None
        session['sign_up_error']= None
        
    # Only allow registering while user is logged out
        if request.method == 'POST':
            account_name = request.form.get('account_name')
            user_name = request.form.get('user_name')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            # Get all information entered by user in the form
            
            cursor = get_db().cursor()
            query = "SELECT * FROM user WHERE account_name = ?;"
            # Is user already exist?
            
            cursor.execute(query, (account_name,))
            user = cursor.fetchall()
            
            if user:
            # If user already exist, then don't register for a new account
                session['sign_up_error'] = 'Account Name already exist, please use a different Account Name'
                
            elif len(account_name) < 6:
            # Account name too short
                session['sign_up_error'] = 'Account name must be at least 6 characters.'
            
            elif len(account_name) > 15:
                # Account name too short
                session['sign_up_error'] = 'Account name must be less than 16 characters.'
            
            elif ' ' in account_name: 
                session['sign_up_error'] = "Account name shouldn't have space(s)"
                
            elif len(user_name)<2:
            # Nickname too short
                session['sign_up_error'] = 'User name must be at least 2 characters.'
                
            elif len(user_name)>15:
                # Nickname too short
                session['sign_up_error'] = 'User name must be at less than 16 characters.'
            
            elif ' ' in user_name: 
                session['sign_up_error'] = "User name shouldn't have space(s)"
            
            elif password1 != password2:
            # Passwords aren't even matching
                session['sign_up_error'] = 'Password don\'t match.'
                
            elif len(password1)<6:
            # Password too short
                session['sign_up_error'] = 'Password must be at least 6 characters.'
                
            elif len(password1)>15:
                # Password too short
                session['sign_up_error'] = 'Password must be less than 16 characters.'
                
            else:
                session['account_name'] = account_name
                session['user_name'] = user_name
                session['password1'] = password1
                # Session them so I can pass the data down to the next route

                #Add user to database
                return redirect(url_for('auth.add'))

        return render_template('login.html')
        # If account is not created, i.e. failed to create one, then keep them on sign_up page
    else:
        return redirect(url_for('views.home'))
        # If they were already logged in, they should be in the home page

@auth.route("/add", methods=["GET", "POST"])
def add():
    cursor = get_db().cursor()
    query = "INSERT INTO user (account_name, password, user_name) VALUES (?,?,?);"
    # Add value of session['account_name'] in the database column account_name
    # Correspondingly, password and user_name, since both passwords are the same, just use the first one

    cursor.execute(query, (session['account_name'], generate_password_hash(session['password1'], method='sha256'),session['user_name'],))
    get_db().commit()
    # Save it
    
    query = "SELECT * FROM user WHERE account_name = ?;"
    cursor.execute(query, (session['account_name'],))
    user = cursor.fetchall()
    session['user_id'] = user[0][0]
    # The user id of the user is passed to the 'views'
    
    session['login'] = True
    # User is logged in
    
    return redirect(url_for('views.home'))
    # Now go to home page
    
@auth.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == 'POST':
        cursor = get_db().cursor()
        query = "SELECT account_name, user_name, password FROM user WHERE id = ?"
        cursor.execute(query,(session['user_id'],))
        setting_user_information = cursor.fetchall()
        session['setting_account_name'] = setting_user_information[0][0]
        session['setting_user_name'] = setting_user_information[0][1]
        session['setting_password'] = setting_user_information[0][2]
        
        
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        
        # This 2 lines doesn't matter, it's just here to remind this 2 variavles are the "flash messages"
        error = 'none'
        success = 'none'
        
        if check_password_hash(session['setting_password'], old_password):
        # If the old password entered correctly

            if new_password == '':
            # No input for old password
                session['update_message'] = 'Please enter your new password.'
                error = 'type1'
                
            elif confirm_new_password == '':
                # No input for old password
                session['update_message'] = 'Please confirm your new password.'
                error = 'type1'
                
            elif new_password != confirm_new_password:
            # If the two new passwords are different
                session['update_message'] = 'Your confirm password is not the same as your new password, please check again.'
                error = 'type2'
                
            elif check_password_hash(session['setting_password'], new_password):
            # If the new password is literally the original password
                session['update_message'] = 'Your new password can\'t be the same as your original, please change your new password.'
                error = 'type2'
                
            else:
            # So old password correct, the two new passwords are the same, and the new is not the old, then it's fine
            # However the password must be at least 6 characters
                if len(new_password)<6:
                # Password too short
                    session['update_message'] = 'Password must be at least 6 characters.'
                    error = 'type1'
                    
                else:
                # Finally everything is good
                    cursor = get_db().cursor()
                    query = "UPDATE user SET password = ? WHERE id = ?"
                    cursor.execute(query, (generate_password_hash(new_password), session['user_id'],))
                    get_db().commit()
                    session['update_message'] = 'Password Changed Successfully'
                    success = 'exist'
                
        elif old_password == '':
        # No input for old password
            session['update_message'] = 'Please enter your old password.'
            error = 'type1'
            
        else:
        # Incorrect old password
            session['update_message'] = 'Incorrect old password, please try again.'
            error = 'type1'
            
    return render_template('setting.html', error = error, success = success)
