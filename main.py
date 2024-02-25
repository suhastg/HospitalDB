from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)

from src.database import get_db_con
from src.models.lab_report import Lab_Report

def get_cookie(request):
    return request.cookies.get('login_cookie')

def extract_cookie_data(cookie):
    cookie_data = {}

    [id, name, user_type] = cookie.split(":")
    cookie_data['id'] = id
    cookie_data['name'] = name
    cookie_data['user_type'] = user_type

    return cookie_data

def get_base_data(request):
    cookie = get_cookie(request)
    data = {'is_login': cookie != None}
    print(f'{data=}')
    return data

@app.route("/")
def index():
    data = get_base_data(request)

    return render_template("index.html", program_data = data)


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
            connection.commit()

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
    
    response = make_response(redirect(url_for("index")))
    response.set_cookie("login_cookie", f'{data["patients"]["patient_id"]}:{data["patients"]["email"]}:patient')
    return response

@app.route("/doctor_login")
def doctor_login_route():
    return render_template("doctor_login.html")

@app.route("/doctor_login_handle", methods=["POST"])
def doctor_login_handle():

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
            query = "SELECT * FROM `doctor` where `email`=%s and `dob`=%s;"
            cursor.execute(query, (Email, Dob))
            result = cursor.fetchone()
            data["doctor"] = result
            print(f"{result=}")
    finally:
        connection.close()

    if data["doctor"] == None:
        return "login failed"
    
    response = make_response(redirect(url_for("index")))
    response.set_cookie("login_cookie", f'{data["doctor"]["doctor_id"]}:{data["doctor"]["email"]}:doctor')
    return response

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    response.set_cookie("login_cookie", '', expires=0)

    return response

@app.route("/consult")
def consult_route():
    data = get_base_data(request)

    connection = get_db_con()
    result = []

    try:
        with connection.cursor() as cursor:
            # Create a new record
            query = "SELECT * FROM `doctor`"
            cursor.execute(query)
            result = cursor.fetchall()
            data["doctors"] = result
            print(f"{result=}")
    finally:
        connection.close()

    return render_template("consult.html",  program_data = data)


@app.route("/consult_handle")
def consult_handle():
    data = get_base_data(request)

@app.route("/lab_report")
def lab_report_route():
    data = get_base_data(request)

    connection = get_db_con()
    result = []

    try: 
        with connection.cursor() as cursor:
            # Create a new record
            query = "SELECT * FROM `lab_report` where `patient_id` = %s;"
            cursor.execute(query, (1))
            result = cursor.fetchall()
            data["lab_reports"] = result
            print(f"{data=}")
    finally:
        connection.close()
    return render_template("lab_report.html",  program_data = data)