"""
Note:
    - Will need to install pytest to run test.
    - Run "pytest" in terminal to run all test cases in respective test files.
"""

"""
Author:
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
def user(initialise_db):
    from app import user
    test_user = user.User(
        name = "javier_learner",
        phone_number = "123456",
        email = "abc@gmail.com",
        password = 'javier_learner',
        user_role_id = '3',
        job_title ='Junior Engineer'
    )
    test_hr = user.User(
        name = "admin",
        phone_number = "123456",
        email = "abc@gmail.com",
        password = "admin",
        user_role_id = '1',
        job_title ='HR'
    )

    db.session.add(test_user)
    db.session.add(test_hr)
    db.session.commit()
    return test_user,test_hr 


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

@pytest.fixture(autouse=True)
def section(group):
    from app import course_section
    group_id = group.id
    test_section = course_section.CourseSection(
        group_id = group_id,
        name ="testCourseSection",
        description = "testing for section"
    )
    db.session.add(test_section)
    db.session.commit()
    return test_section



def tearDown(): 
    print('\n Tearing Down')
    from app import course, group, user, enrolment_request,course_section
    db.session.query(group.Group).delete()
    db.session.query(course_section.CourseSection).delete()
    db.session.query(user.User).delete()
    db.session.query(enrolment_request.EnrolmentRequest).delete()
    db.session.query(course.Course).delete()
    db.session.commit()
    print('\n Tearing Down Complete')





##############################
####### Javier's Part ########
##############################


### Creation of Enrolment Requests with All Conditions Satisfied ###
def test_create_enrolment_request(group,user):
    with app.test_client() as test_client:
        response = test_client.post('/enrolment_request',
                            data = json.dumps({
                                "user_id": user[0].id,
                                "group_id" : group.id
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 200
        global enrolment_request
        enrolment_request = response.get_json()['data']

## View Pending Enrolment Requests by Learners ID ###
def test_learner_enrolment_request():
    with app.test_client() as test_client:
        user_id =enrolment_request['user_id']
        response = test_client.get(f'/enrolment_request/learner/{user_id}')
        assert response.status_code == 200
        

### View All Pending  Enrolment Requests ###
def test_pending_enrolment_request():
    with app.test_client() as test_client:
        response = test_client.get('/enrolment_request')
        assert response.status_code == 200 
        pending_requests = response.get_json()['data']
        assert len(pending_requests) > 0





# Approve Enrolment Requests ###
def test_approve_requests(user):
    with app.test_client() as test_client:
        # print(user[1].id)
        print(f"/enrolment_request/approve/{enrolment_request['id']}")
        response = test_client.put(f"/enrolment_request/approve/{enrolment_request['id']}",
                            data = json.dumps({
                                "approved_by": user[1].id
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )                        
        print(response.get_json())
        assert response.status_code == 200

# Delete Enrolment Request ###
def test_delete_requests():
    with app.test_client() as test_client:
        response = test_client.delete(f"/enrolment_request/user/{enrolment_request['user_id']}")
        assert response.status_code == 200








