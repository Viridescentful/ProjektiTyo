from dotenv import load_dotenv
from dotenv import dotenv_values
import os

load_dotenv()

import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            port=3306,
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            autocommit=True
        )

    def get_conn(self):
        return self.conn
