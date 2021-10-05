import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager



app = Flask(__name__)
CORS(app)

db_host = os.environ.get("DB_HOSTNAME")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/lms"
db = SQLAlchemy(app)
login_manager = LoginManager()
import dbsample  # # import the name of the file containing that module
import login

@app.route("/test", methods=['GET'])
def test():

    return jsonify(
        {
            "code": 200,
            "data": "test"
        }
    ), 200

os.environ["FLASK_RUN_FROM_CLI"] = "false"
app.run(host='0.0.0.0', port=8000, debug=True)
 