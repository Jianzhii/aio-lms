"""
Note:
    - Will need to install pytest to run test.
    - Run "pytest" in terminal to run all test cases in respective test files.
"""

"""
Author:
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


def tearDown(): 
    print('\n Tearing Down')
    from app import course, group, course_section    
    db.session.query(course_section.CourseSection).delete()
    db.session.query(group.Group).delete()
    db.session.query(course.Course).delete()
    db.session.commit()
    print('\n Tearing Down Complete')

# Test cases
def test_create_course(course):
    with app.test_client() as test_client:
        response = test_client.post('/course',
                            data = json.dumps({
                                "course_id": course.id,
                                "name": "Engineering Basics 201",
                                "description": "Test Creation of Course"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 200
        global section
        section = response.get_json()['data']

def test_get_one_course():
    with app.test_client() as test_client:
        response = test_client.get(f"/course/{course['id']}")
        assert response.status_code == 200

def test_update_course():
    update_description = "Test Edit Course Details"
    with app.test_client() as test_client:
        response = test_client.put('/course',
                            data = json.dumps({
                                "id": course['id'],
                                "name": "Engineering Basics 201",
                                "description": update_description
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 200

        retrieve_course = test_client.get(f"/course/{course['id']}")
        assert retrieve_course.get_json()['data']['description'] == update_description 

def test_delete_course():
    with app.test_client() as test_client:
        response = test_client.delete(f"/course_/{course['id']}")
        assert response.status_code == 200
        tearDown()