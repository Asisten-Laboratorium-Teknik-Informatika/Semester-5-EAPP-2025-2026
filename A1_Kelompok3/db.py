# import mysql.connector
import pymysql
from pymysql.cursors import DictCursor

def get_connection():
    # return mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="", 
    #     database="smartpay"
    # )
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="smartpay",
        cursorclass=DictCursor
    )
