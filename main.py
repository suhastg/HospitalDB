from flask import Flask, render_template, request, redirect, url_for, make_response, abort

app = Flask(__name__)

from src.database import get_db_con
from src.models.lab_report import Lab_Report

consult_timings = [
    {"cid": 1, "time": "10:00 am", "sql_time": "10:00:00"},
    {"cid": 2, "time": "10:30 am", "sql_time": "10:30:00"},
    {"cid": 3, "time": "11:00 am", "sql_time": "11:00:00"},
    {"cid": 4, "time": "11:30 am", "sql_time": "11:30:00"},
    {"cid": 5, "time": "12:00 pm", "sql_time": "12:00:00"},
    {"cid": 6, "time": "12:30 pm", "sql_time": "12:30:00"},
    {"cid": 7, "time": "2:00 pm", "sql_time": "14:00:00"},
    {"cid": 8, "time": "2:30 pm", "sql_time": "14:30:00"},
    {"cid": 9, "time": "3:00 pm", "sql_time": "15:00:00"},
    {"cid": 10, "time": "3:30 pm", "sql_time": "15:30:00"},
    {"cid": 11, "time": "4:00 pm", "sql_time": "16:00:00"},
    {"cid": 12, "time": "4:30 pm", "sql_time": "16:30:00"}
]


def get_cookie(request):
    return request.cookies.get('login_cookie')


def extract_cookie_data(cookie):
    
    if cookie is None:
        return None

    cookie_data = {}

    [id, email, user_type] = cookie.split(":")
    cookie_data['id'] = id
    cookie_data['email'] = email
    cookie_data['user_type'] = user_type

    return cookie_data


def get_base_data(request):
    cookie = get_cookie(request)
    cookie_data = extract_cookie_data(cookie)

    if cookie:
        data = {'is_login': True, 'user_type': cookie_data['user_type'], "id": cookie_data["id"]}
    else:
        data = {'is_login': False, 'user_type': None}
    print(f'{data=}')
    return data


@app.route("/")
def index():
    data = get_base_data(request)
    cookie = get_cookie(request)

    return render_template("index.html", program_data = data)


@app.errorhandler(404)
def wrong_turn_mate(request):
    return render_template("404.html"), 404

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
    data = get_base_data(request)
    return render_template("login.html",  program_data = data)


@app.route("/login_handle", methods=["POST"])
def login_handle():

    Dob=request.form['dob']
    Email=request.form['email']

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
    data = get_base_data(request)
    return render_template("doctor_login.html",  program_data = data)


@app.route("/doctor_login_handle", methods=["POST"])
def doctor_login_handle():

    Dob=request.form['dob']
    Email=request.form['email']

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

    if data == None or data['user_type'] != 'patient':
        print(f'{data=}')
        return abort(404)

    connection = get_db_con()
    result = []
    data["consult_timings"] = consult_timings
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


@app.route("/consult_handle", methods=["POST"])
def consult_handle():
    data = get_base_data(request)
    connection = get_db_con()
    form = request.form

    [doctor_id, consult_date, consult_time] = [form.get('doctor'), form.get('consult_date'), form.get('consult_time')]

    print(f'{doctor_id=}, {consult_date=}, {consult_time=}')
    sql_dt = f'{consult_date} {consult_timings[int(consult_time)-1]["sql_time"]}'
    print(f'{sql_dt}')
    
    try:
        with connection.cursor() as cursor:
            query="""
                SELECT COUNT(*) AS availability 
                FROM `consultation` c 
                WHERE c.`consult_date` = %s 
                AND c.`doctor_id` = %s 
                AND NOT EXISTS (
                    SELECT 1 FROM `consultation` c2    
                    WHERE c2.`consult_date` = %s    
                    AND c2.`patient_id` =  %s
                );
            """
            cursor.execute(query, (sql_dt, int(doctor_id), sql_dt, int(data["id"])))
            result = cursor.fetchall()
            print(f"{result=}")
            if result[0]["availability"] == 10:
                q = "INSERT INTO `consultation`(`patient_id`, `doctor_id`, `consult_date`, `fees`) VALUES (%s,%s,%s,%s)"
                cursor.execute(q,(data["id"],doctor_id,sql_dt,1000))
                connection.commit()
            # print(f"{result=}")
    finally:
        connection.close()

    return redirect(url_for("index"))
    

@app.route("/lab_report")
def lab_report_route():
    data = get_base_data(request)

    connection = get_db_con()
    result = []

    cookie_data = extract_cookie_data(get_cookie(request))

    try: 
        with connection.cursor() as cursor:
            if data["user_type"] == "paitent":
                query = "SELECT * FROM `lab_report` where `patient_id` = %s;"
            else:
                query = "SELECT * FROM `lab_report` where `doctor_id` = %s;"
            
            cursor.execute(query, (cookie_data["id"]))
            result = cursor.fetchall()
            data["lab_reports"] = result
            print(f"{data=}")
    finally:
        connection.close()
    return render_template("lab_report.html",  program_data = data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)