import psycopg2
from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

conn = psycopg2.connect(
    dbname = "plumedata",
    user = "app_user",
    password = "user_password",
    host = "localhost"
)

cursor = conn.cursor()




