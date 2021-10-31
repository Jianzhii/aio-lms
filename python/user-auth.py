from flask import jsonify

from app import app, db


@app.route("/login", methods=["POST"])
def test():

    return jsonify({"code": 200, "data": "test"}), 200
