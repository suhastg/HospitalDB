from flask import Flask, render_template

app = Flask(__name__)

DB_URL = "mysql://root@localhost:3306/hospitaldb"

import pymysql.cursors
import pymysql

def get_db_con():
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                user='root',
                db='hospitaldb',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
    return connection


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

    return render_template("index.html", data1=data)