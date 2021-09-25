
from flask import jsonify
from __main__ import app
import os
from flask_sqlalchemy import SQLAlchemy

db_host = os.environ.get("DB_HOSTNAME")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/lms"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100),nullable=False)
    user_role_id = db.Column(db.Integer, nullable=False)
    job_title = db.Column(db.String(45), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'user_role_id': self.user_role_id,
            'job_title': self.job_title
        }

class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'role_name': self.role_name,
        }

@app.route("/user", methods=['GET'])
def alluser():
    users = User.query.all()
    return jsonify(
        {
            "code": 200,
            "data": [user.json() for user in users]
        }
    ), 200

# TODO
@app.route("/user_one", methods=['GET'])
def userwithrole():
    users = db.session.query(User, UserRole)\
            .join(UserRole, UserRole.id == User.user_role_id).all()
    for row in users:
        print("(")
        for item in row:
            print("   ", item)
        print(")")
    return jsonify(
        {
            "code": 200,
            "data": "Asd"
        }
    ), 200

# to jsonify results from joined tables TODO
def to_json(query_results):
    result = []
    for row in query_results:
        row_item = {}
        for item in row:
            print("   ", item)
    return result
