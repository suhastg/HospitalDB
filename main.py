from flask import Flask

app = Flask(__name__)

DB_URL = "mysql://root@localhost:3306/hospitaldb"

import pymysql.cursors
import pymysql

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             db='hospitaldb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Create a new record
        query = "SELECT * FROM patient"
        cursor.execute(query)
        result = cursor.fetchall()
        print(f"{result=}")
finally:
    connection.close()

@app.route("/")
def hello_world():
    return (
    """<p>
    <input type = "text" />
    </p>""")