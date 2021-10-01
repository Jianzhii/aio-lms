from __main__ import app, db
from flask import jsonify

@app.route("/login", methods=['POST'])
def test():

    return jsonify(
        {
            "code": 200,
            "data": "test"
        }
    ), 200
