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


# Set up app and connection to DB
def load_env():
    load_dotenv()


db_host = os.environ.get("DB_HOSTNAME")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/lms"




##############################
####### Javier's Part ########
##############################

### View All Pending  Enrolment Requests ###
def test_pending_enrolment_request():
    with app.test_client() as test_client:
        response = test_client.get('/enrolment_request')
        assert response.status_code == 200 

### View Pending Enrolment Requests by Learners ID ###
def test_learner_enrolment_request():
    with app.test_client() as test_client:
        response = test_client.get('/enrolment_request/learner/6')
        assert response.status_code == 200

### Creation of Enrolment Requests with All Conditions Satisfied ###
def test_create_enrolment_request():
    with app.test_client() as test_client:
        body =\
        {
            "user_id" : 18,
            "group_id":3
        }
        response = test_client.post('/enrolment_request',json=body)
        assert response.status_code == 200
        delete_response = test_client.delete('/enrolment_request/user/18')
        assert delete_response.status_code == 200


### Check Creation of Enrolment Request if not within enrolment period of the group ###
def test_check_enrolment_period():
    with app.test_client() as test_client:
        body =\
        {
            "user_id" : 15,
            "group_id":15
        }
        response = test_client.post('/enrolment_request',json=body)
        assert response.status_code == 406

### Check creation of enrolment request if learner has already enrolled into an ongoing course ###
def test_check_enrolment_ongoing_course():
    with app.test_client() as test_client:
        body =\
        {
            "user_id" : 7,
            "group_id":1
        }
        response = test_client.post('/enrolment_request',json=body)
        assert response.status_code == 407

### Check creation of enrolment request if group size is full ###
def test_check_group_size():
    with app.test_client() as test_client:
        body =\
        {
            "user_id" : 14,
            "group_id":88
        }
        response = test_client.post('/enrolment_request',json=body)
        assert response.status_code == 406


### Delete Enrolment Request ###
def test_delete_requests():
    with app.test_client() as test_client:
        body =\
        {
            "user_id" : 19,
            "group_id":3
        }
        response = test_client.post('/enrolment_request',json=body)
        assert response.status_code == 200
        delete_response = test_client.delete('/enrolment_request/user/19')
        assert delete_response.status_code == 200


# ### Approve Enrolment Requests ###
# def test_approve_requests():
#     with app.test_client() as test_client:
#         body =\
#         {
#             "approved_by" : 1
#         }
#         response = test_client.put('/enrolment_request/approve/68',json=body)
#         assert response.status_code == 200




