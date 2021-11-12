"""
Note:
    - Will need to install pytest to run test.
    - Run "pytest" in terminal to run all test cases in respective test files.
"""

"""
Author: Chua Ruo Lin
"""

import os

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


#   Set up connection to DB
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


# Set up test data in database
@pytest.fixture(autouse=True)
def course(initialise_db):
    from app import course
    test_course = course.Course(
        name = "Test Course",
        description = "Test Description",
        prerequisite = []
    )
    db.session.add(test_course)
    db.session.commit()
    return test_course


def tearDown(): 
    print('\n Tearing Down')
    from app import course, group
    db.session.query(group.Group).delete()
    db.session.query(course.Course).delete()
    db.session.commit()
    print('\n Tearing Down Complete')


# Creation of Group
def test_create_group(course):    
    start_date = datetime.now() + timedelta(days=50)
    end_date = datetime.now() + timedelta(days=80)
    enrol_start_date = datetime.now() - timedelta(days=10)
    enrol_end_date = datetime.now() + timedelta(days=30)
    with app.test_client() as test_client:
        response = test_client.post('/group',
                        data = json.dumps({
                            "course_id": course.id,
                            "size": 30,
                            "start_date": start_date.strftime("%Y/%m/%d, %H:%M:%S"),
                            "end_date": end_date.strftime("%Y/%m/%d, %H:%M:%S"),
                            "enrol_start_date": enrol_start_date.strftime("%Y/%m/%d, %H:%M:%S"),
                            "enrol_end_date": enrol_end_date.strftime("%Y/%m/%d, %H:%M:%S"),
                            "trainer_id": 2
                        }),
                        headers = {
                            "Content-Type": "application/json"
                        }
        )
        assert response.status_code == 200
        global group
        group = response.get_json()['data']


# Get details of one Group
def test_get_one_group():
    with app.test_client() as test_client:
        response = test_client.get(f"/group/{group['id']}")
        assert response.status_code == 200


# Delete one Group
def test_delete_one_group():
    with app.test_client() as test_client:
        response = test_client.delete(f"/group/{group['id']}")
        assert response.status_code == 200
        tearDown()
