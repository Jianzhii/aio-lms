from app import app, db
from flask import jsonify, request
from dbsample import User

# Login API endpoint implementation
# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        data = request.get_json()
        print(data)
        _username = data['username']
        _password = data['password']
        row = User.query.filter_by(name=_username).first()
        print(row)
        return "asdsadssa"
    except Exception as e:
        return e

 
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return