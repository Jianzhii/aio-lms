import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

CORS(app)

db_host = os.environ.get("DB_HOSTNAME")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/lms"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Importing all modules
import login
import user
import course
import group
import course_section
import enrol
import enrolment_request
import forum
import chat
import upload
import section_progress
import add_quiz


@app.route("/test", methods=["GET"])
def test():

    return jsonify(
        {
            "code": 200,
            "data": "test"
        }
    ), 200
