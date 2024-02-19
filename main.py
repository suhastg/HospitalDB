from flask import Flask, render_template

app = Flask(__name__)

from src.database import get_db_con

program_state = {}

program_state["is_login"] = True

@app.route("/")
def index():

    connection = get_db_con()
    result = []

    data = {}

    try: 
        with connection.cursor() as cursor:
            # Create a new record
            query = "SELECT * FROM patient"
            cursor.execute(query)
            result = cursor.fetchall()
            data["patients"] = result
    finally:
        connection.close()

    return render_template("index.html", program_data = program_state)


@app.route("/signup")
def signup_route():
    return render_template("signup.html")

@app.route("/login")
def login_route():
    return render_template("login.html")

@app.route("/consult")
def consult_route():
    return render_template("consult.html",  program_data = program_state)