"""
Note:
    - Will need to install pytest to run test.
    - Run "pytest" in terminal to run all test cases in respective test files.
"""

"""
Author: Kendrick Yeong
"""

import os
from _pytest.fixtures import fixture

from app import app
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytest
from flask import json
from flask_sqlalchemy import SQLAlchemy


#  Load function to read from .env
@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


# Set up connection to DB
@pytest.fixture(autouse=True)
def initialise_db():
    db_host = os.environ.get("DB_HOSTNAME")
    db_port = os.environ.get("DB_PORT")
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/lms_test"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    global db
    db = SQLAlchemy(app)
    return db

#settings up the course if not it can't be ran
@pytest.fixture(autouse=True)
def course(initialise_db):
    print('course')
    from app import course
    test_course = course.Course(
        name = "Test Course",
        description = "Test Description",
        prerequisite = []
    )
    db.session.add(test_course)
    db.session.commit()
    return test_course

@pytest.fixture(autouse=True)
def group(course):
    from app import group
    course_id = course.id
    test_group = group.Group(
        course_id = course_id,
        start_date = datetime.now() + timedelta(days=50),
        end_date = datetime.now() + timedelta(days=80),
        enrol_start_date = datetime.now() - timedelta(days=10),
        enrol_end_date = datetime.now() + timedelta(days=30),
        size = 50
    )
    db.session.add(test_group)
    db.session.commit()
    return test_group

#Deleting all entries into the db
def tearDown(): 
    print('\n Tearing Down')
    from app import course, group, group_quiz    
    db.session.query(group_quiz.GroupQuiz).delete()
    db.session.query(group.Group).delete()
    db.session.query(course.Course).delete()
    db.session.commit()
    print('\n Tearing Down Complete')

# Creating the Quiz
def test_create_quiz(group):
    with app.test_client() as test_client:
        response = test_client.post('/group_quiz',
                            data = json.dumps([{
                                "group_id": group.id,
                                "question_no": 10,
                                "question": "Am i right or wrong",
                                "choice": ["Yes","OfCuz"],
                                "answer": "OfCuz",
                                "duration": 2000
                            }]),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        print(response.get_json())
        assert response.status_code == 200
        global quiz
        quiz = response.get_json()['data']


def test_validate_quiz():
    with app.test_client() as test_client:
        response = test_client.post()

def test_delete_section():
    with app.test_client() as test_client:
        tearDown()