from flask import Flask, render_template, request, redirect, url_for, make_response, abort, g

app = Flask(__name__)

from .database import get_db_con
from .models.lab_report import Lab_Report
from .middleware import login_mw, patient_only, doctor_only
from .utils import get_base_data, get_cookie

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

lab_report_types = [
    {"rid": 1, "type": "Blood Test"},
    {"rid": 2, "type": "Eye Test"},
    {"rid": 3, "type": "Ear Test"},
    {"rid": 4, "type": "Urine Test"},
    {"rid": 5, "type": "X Ray"}
]


@app.errorhandler(404)
def wrong_turn_mate(request):
    return render_template("404.html"), 404


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
@login_mw
def consult_route():
    data = g.data

    if g.data["user_type"] == "doctor":
        return redirect(url_for("consultation"))

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
@login_mw
@patient_only
def consult_handle():
    data = g.data
    connection = get_db_con()
    form = request.form

    [doctor_id, consult_date, consult_time] = [form.get('doctor'), form.get('consult_date'), form.get('consult_time')]

    print(f'{doctor_id=}, {consult_date=}, {consult_time=}')
    sql_dt = f'{consult_date} {consult_timings[int(consult_time)-1]["sql_time"]}'
    print(f'{sql_dt}')
    
    try:
        with connection.cursor() as cursor:
            # checking availability of doctor and patent on given date and time
            query="""
                select count(*) as availability
                where not EXISTS (
                    select 1 from consultation c
                    where c.consult_date = %s
                    and c.doctor_id = %s
                ) and not EXISTS (
                    select 1 from consultation c
                    where c.consult_date = %s
                    and c.patient_id = %s
                )
            """
            cursor.execute(query, (sql_dt, int(doctor_id), sql_dt, int(data["id"])))
            result = cursor.fetchall()
            print(f"{result=}")
            if result[0]["availability"] == 1:

                query = "SELECT fees from `doctor` where doctor_id = %s"
                cursor.execute(query, (doctor_id))
                result = cursor.fetchone()
                print(f"{result=}")
                fee = result["fees"]

                q = "INSERT INTO `consultation`(`patient_id`, `doctor_id`, `consult_date`, `fees`) VALUES (%s,%s,%s,%s)"
                cursor.execute(q,(data["id"],doctor_id,sql_dt,fee))
                connection.commit()
            # print(f"{result=}")
    finally:
        connection.close()

    return redirect(url_for("index"))


@app.route("/consultation")
@login_mw
@doctor_only
def consultation():
    data = g.data

    connection = get_db_con()
    result = []

    try:
        with connection.cursor() as cursor:
            # selecting consultation records that are in the future and still yet to be attended
            query = """
                    SELECT c.consult_id, p.name, c.consult_date, c.fees
                    FROM consultation c, patient p
                    WHERE c.doctor_id = %s
                    and c.patient_id = p.patient_id
                    and consult_date>= now() and  c.consult_id not in (
                        SELECT pr.consult_id 
                        from patient_report pr, 
                        consultation co
                        where pr.consult_id = co.consult_id and
                        co.doctor_id = %s
                    )
                    order by c.consult_date;
                    """
            cursor.execute(query, (g.data["id"], g.data["id"]))
            result = cursor.fetchall()
    finally:
        connection.close()

    print(f"{result=}")
    data["consultations"] = result
    return render_template("consultation.html", program_data = data)



@app.route("/lab_report")
@login_mw
def lab_report_route():
    data = g.data

    connection = get_db_con()
    result = []

    try:
        with connection.cursor() as cursor:
            if data["user_type"] == "patient":
                f = "p.patient_id = %s"
            else:
                f = "d.doctor_id = %s"
            
            
            query = f"""
                        SELECT lr.report_id, c.consult_id, p.name as p_name, d.name as d_name, lr.report_type, lr.fee
                        FROM `lab_report` lr,
                        `consultation` c,
                        `patient` p,
                        `doctor` d
                        where lr.consult_id = c.consult_id
                        and c.doctor_id = d.doctor_id
                        and c.patient_id = p.patient_id
                        and {f}
                        and lr.consult_id not in (select consult_id from patient_report);
                    """
            
            cursor.execute(query, (data["id"]))
            result = cursor.fetchall()
            data["lab_reports"] = result
            print(f"{data=}")
    finally:
        connection.close()
    return render_template("lab_report.html",  program_data = data)


@app.route("/generate_lab_report/<int:id>")
@login_mw
@doctor_only
def generate_lab_report(id: int):
    data = g.data
    data["lab_report_types"] = lab_report_types

    connection = get_db_con()
    result = []

    try:
        with connection.cursor() as cursor:
            query = """
                    SELECT c.consult_id, p.name, p.patient_id, doctor_id
                    from `consultation` c, `patient` p
                    where c.consult_id = %s
                    and p.patient_id = c.patient_id
                    """
            cursor.execute(query, (id))
            result = cursor.fetchall()
            data["paitent_data"] = result[0]
            print(f"{data=}")
    finally:
        connection.close()


    return render_template("generate_lab_report.html", program_data = data)


@app.route("/handel_generate_lab_report", methods=["POST"])
@login_mw
def handel_generate_lab_report():
    connection = get_db_con()
    form = request.form

    print(f"{form=}")
    [consult_id, report_type, fee] = [form.get("consult_id"), int(form.get("report")), float(form.get("fee"))]

    try:
        with connection.cursor() as cursor:
            query = """INSERT INTO `lab_report`(`consult_id`, `report_type`, `fee`) VALUES (%s, %s, %s)"""
            cursor.execute(query, (consult_id, lab_report_types[report_type - 1]['type'], fee))
            connection.commit()
    finally:
        connection.close()

    return redirect(url_for("index"))


@app.route("/attend/<int:id>")
@login_mw
@doctor_only
def Attend_patient(id: int):
    data = g.data

    connection = get_db_con()
    result = []
    data["consult_id"] = id

    try:
        with connection.cursor() as cursor:
            query = """
                    SELECT p.name
                    from `consultation` c, `patient` p
                    where c.consult_id = %s
                    and p.patient_id = c.patient_id
                    """
            cursor.execute(query, (id))
            result = cursor.fetchone()
            data["paitent_name"] = result["name"]

            query = """
                    select report_id, report_type
                    from lab_report
                    where consult_id = %s
                    """
            cursor.execute(query, (id))
            result = cursor.fetchall()
            data["lab_reports"] = result

            print(f"{data=}")
    finally:
        connection.close()


    return render_template("attend.html", program_data = data)

@app.route("/handel_attend_patient", methods=["POST"])
@login_mw
def handel_attend_patient():
    connection = get_db_con()
    form = request.form

    print(f"{form=}")
    [consult_id, message, medicine] = [form.get("consult_id"), form.get("message"), form.get("medicine")]

    try:
        with connection.cursor() as cursor:
            query = """INSERT INTO `patient_report`(`consult_id`, `doctor_msg`, `medicine`) VALUES (%s,%s,%s)"""
            cursor.execute(query, (consult_id, message, medicine))
            connection.commit()
    finally:
        connection.close()

    return redirect(url_for("index"))

@app.route("/report")
@login_mw
def report():
    data = g.data
    connection = get_db_con()
    data["report"] = []

    try:
        with connection.cursor() as cursor:

            if data["user_type"] == "doctor":
                f = "d.doctor_id = %s"
            else:
                f = "p.patient_id = %s"

            query = f"""
            select co.consult_id, p.name as patient_name, d.name as doctor_name, 
            pr.doctor_msg as message, pr.medicine, co.fees
            FROM patient_report pr, consultation co, doctor d, patient p
            where pr.consult_id = co.consult_id AND
            d.doctor_id = co.doctor_id AND
            p.patient_id = co.patient_id AND
            {f};
            """
            cursor.execute(query, (data["id"]))
            patient_report = cursor.fetchall()
            print(f"{patient_report=}")

            if len(patient_report) == 0:
                raise ValueError('skip this part.')
            
            s = slice(1, -1)
            cdi = f"{[r['consult_id'] for r in patient_report]}"
            print(f"{cdi[s]=}")

            query = """select report_id, consult_id, report_type from lab_report where consult_id in (%s)"""
            cursor.execute(query, (cdi[s]))
            lab_report = cursor.fetchall()
            print(f"{lab_report=}")

            data["report"] = [
                {
                    "consult_id": pr["consult_id"], 
                    "patient_name": pr["patient_name"], 
                    "doctor_name": pr["doctor_name"], 
                    "message": pr["message"], 
                    "medicine": pr["medicine"], 
                    "reports": [{"report_id": lr["report_id"], "report_type": lr["report_type"]} for lr in lab_report if lr["consult_id"] == pr["consult_id"]]
                } for pr in patient_report]
    except ValueError:
        pass
    finally:
        connection.close()

    print(f"{data=}")

    return render_template("report.html", program_data = data)

@app.route("/report/<int:id>")
@login_mw
def handle_report(id: int):
    data = g.data
    connection = get_db_con()
    data["report"] = []

    try:
        with connection.cursor() as cursor:

            query = """
            select co.consult_id, p.name as patient_name, d.name as doctor_name, 
            pr.doctor_msg as message, pr.medicine, co.fees
            FROM patient_report pr, consultation co, doctor d, patient p
            where pr.consult_id = co.consult_id AND
            d.doctor_id = co.doctor_id AND
            p.patient_id = co.patient_id AND
            co.consult_id = %s
            """
            cursor.execute(query, (id))
            patient_report = cursor.fetchall()

            if len(patient_report) == 0:
                raise ValueError('skip this part.')

            query = """select report_id, consult_id, report_type, fee from lab_report where consult_id = %s"""
            cursor.execute(query, (id))
            lab_report = cursor.fetchall()

            data["report"] = [
                {
                    "consult_id": pr["consult_id"], 
                    "patient_name": pr["patient_name"], 
                    "doctor_name": pr["doctor_name"], 
                    "message": pr["message"], 
                    "fees": pr["fees"], 
                    "medicine": pr["medicine"], 
                    "reports": [
                        {
                            "report_id": lr["report_id"], 
                            "report_type": lr["report_type"], 
                            "fees": lr["fee"]
                        } for lr in lab_report if lr["consult_id"] == pr["consult_id"]]
                } for pr in patient_report]
    except ValueError:
        pass
    finally:
        connection.close()

    print(f"{data=}")

    return render_template("patient_report.html", program_data = data)