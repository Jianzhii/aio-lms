
from flask import jsonify
from __main__ import app

@app.route("/login", methods=['POST'])
def login():

    return jsonify(
        {
            "code": 200,
            "data": "this is login"
        }
    ), 200
