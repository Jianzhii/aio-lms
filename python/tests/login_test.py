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
import pytest
from flask import json


#  Load function to read from .env
@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


# Set up connection to DB
@pytest.fixture(autouse=True)
def initalise_db():
    db_host = os.environ.get("DB_HOSTNAME")
    db_port = os.environ.get("DB_PORT")
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/lms"


# Test cases
def test_admin_login():
    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.post('/login',
                            data = json.dumps({
                                "username": "admin",
                                "password": "admin"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 200


def test_incorrect_admin_login():
    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.post('/login',
                            data = json.dumps({
                                "username": "admin",
                                "password": "notadmin"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 406


def test_trainer_login():
    with app.test_client() as test_client:
        response = test_client.post('/login',
                            data = json.dumps({
                                "username": "trainer",
                                "password": "trainer"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 200


def test_incorrect_trainer_login():
    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.post('/login',
                            data = json.dumps({
                                "username": "trainer",
                                "password": "nottrainer"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 406


def test_learner_login():
    with app.test_client() as test_client:
        response = test_client.post('/login',
                            data = json.dumps({
                                "username": "learner",
                                "password": "learner"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 200


def test_incorrect_learner_login():
    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.post('/login',
                            data = json.dumps({
                                "username": "learner",
                                "password": "notlearner"
                            }),
                            headers = {
                                "Content-Type": "application/json"
                            }
                        )
        assert response.status_code == 406
