from flask import Flask, render_template,  request, redirect, url_for

app = Flask(__name__)

from src.database import get_db_con

program_state = {}

program_state["is_login"] = False

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
            # print(f"{result=}")
    finally:
        connection.close()

    return render_template("index.html", program_data = program_state)


@app.route("/signup")
def signup_route():
    return render_template("signup.html")

@app.route("/signup_handle", methods=["POST"])
def signup_handle():
    connection = get_db_con()
    

    # print(f"{request.form}")
    Name=request.form['name']
    Dob=request.form['dob']
    Gender=request.form['gender']
    Email=request.form['email']


    try:
        with connection.cursor() as cursor:
            print(f"{Name=}, {Dob=}, {Gender=}, {Email=}")
            query='INSERT INTO `patient`( `name`, `dob`, `gender`, `email`) VALUES (%s,%s,%s, %s)'
            cursor.execute(query, (Name, Dob, Gender, Email))
    finally:
        cursor.close()

    return redirect(url_for("login_route"))

@app.route("/login")
def login_route():
    return render_template("login.html")

@app.route("/login_handle", methods=["POST"])
def login_handle():

    Dob=request.form['dob']
    Email=request.form['email']
    print(Dob)
    print(Email)

    connection = get_db_con()
    result = []
    data = {}

    try: 
        with connection.cursor() as cursor:
            # Create a new record
            query = "SELECT * FROM `patient` where `email`=%s and `dob`=%s;"
            cursor.execute(query, (Email, Dob))
            result = cursor.fetchone()
            data["patients"] = result
            print(f"{result=}")
    finally:
        connection.close()

    if data["patients"] == None:
        return "login failed"
    
    program_state["is_login"] = True
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    program_state["is_login"] = False
    return redirect(url_for("index"))



@app.route("/consult")
def consult_route():
    return render_template("consult.html",  program_data = program_state)