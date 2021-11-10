from flask import jsonify, request

from app import app, db
from user import User, UserRole


# Login API endpoint implementation
# Route for handling the login page logic
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        _username = data["username"]
        _password = data["password"]
        row = User.query.filter_by(name=_username).first().json()
        if row["password"] == _password:
            role_id = row["user_role_id"]
            userObj = UserRole.query.filter_by(id=role_id).first().json()
            role_name = userObj["role_name"]
            return jsonify(
                    {
                        "code": 200,
                        "msg": "Login Success",
                        "data": {
                            "id": f"{row['id']}",
                            "username": f"{row['name']}",
                            "role_name": f"{role_name}",
                        },
                    }
                ), 200
        else:
            return jsonify(
                {
                    "code": 406,
                    "message": "Invalid Username/password"
                }
            ), 406

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify(
            {
                "code": 406,
                "message": f"Error: {e}"
            }
        ), 406
