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