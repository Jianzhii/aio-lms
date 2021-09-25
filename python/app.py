from flask import Flask, jsonify
import os

app = Flask(__name__)
import dbsample ## import the name of the file containing that module

@app.route("/db_port", methods=['GET'])
def test():

    return jsonify(
        {
            "code": 200,
            "data": os.environ.get("DB_PORT")
        }
    ), 200

app.run(host='0.0.0.0', port=8000, debug=True)