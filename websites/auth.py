from flask import Blueprint, render_template, request

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@auth.route('/logout')
def logout():
    return "<p>logout</p>"

@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    
    if request.method == 'POST':
        account_name = request.form('account_name')
        user_name = request.form('user_name')
        password1 = request.form('password1')
        password2 = request.form('password2')
        
        if len(account_name) < 7:
            pass
        elif len(user_name)<2:
            pass
        elif password1 != password2:
            pass
        elif len(password1)<7:
            pass
        else:
            pass
            #Add user to database
    return render_template('sign_up.html')