from flask import Flask, g, render_template, request, redirect
import sqlite3

# Can it be something else not __name__?
app = Flask(__name__)

DATABASE = "backpack.db"

# How does this work???
def get_db():
    
    # What is gatattr?
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    cursor = get_db().cursor()
    command = "select * FROM contents"
    cursor.execute(command)
    result = cursor.fetchall()
    return render_template("contents.html", result=result)


@app.route("/add", methods=["GET", "POST"])
# By the time you click the "submit button", "Comfirm Add Item", the action of the form will lead to this route
# When you hit the "submit", the "text input", item_name and item_description
# will have their value exactly as the user input
def add():
    cursor = get_db().cursor()
    command = "INSERT INTO contents (name, description) VALUES (?,?)"
    # And in this route, connect to the database

    item_name = request.form["item_name"]
    item_description = request.form["item_description"]
    # Now bring the value of the "text input", the user's input to the python file

    cursor.execute(command, (item_name, item_description))
    get_db().commit()
    return redirect("/")
    # Back to the main page


@app.route("/delete", methods=["GET", "POST"])
def delete():
    print(request)
    if request.method == "POST":

    # This time thing are a bit different that I supposed, like each button for the 'delete' is a submit button
    # When you click the "submit", what happens is the hidden input's value becomes the corresponding 'id'

        cursor = get_db().cursor()
        id = int(request.form["item_id"])
        # Get id from HTML to python file using request.form()

        command = "DELETE FROM contents WHERE id =?"
        cursor.execute(command, (id,))
        get_db().commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
    # Real time update to the web application
