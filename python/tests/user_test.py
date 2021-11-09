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


# Test cases
def test_get_all_user():
    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.get('/test')
        assert response.status_code == 200


def test_get_role():
    with app.test_client() as test_client:
        response = test_client.get('/user_role')
        assert response.status_code == 200


# def test_get_trainer():
#     with app.test_client() as test_client:
#         response = test_client.get('/all_trainer')
#         assert response.status_code == 200
