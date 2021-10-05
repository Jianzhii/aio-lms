from app import app, db
from flask import jsonify

class User(db.Model):
    
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_role_id = db.Column(db.Integer, nullable=False)
    job_title = db.Column(db.String(45), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'password' : self.password,
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
def getAllUser():
    users = User.query.all()
    return jsonify(
        {
            "code": 200,
            "data": [user.json() for user in users]
        }
    ), 200

@app.route("/user_role", methods=['GET'])
def getAllUserWithRole():
    users = db.session.query(User, UserRole)\
            .join(UserRole, UserRole.id == User.user_role_id).all()
    # join query above returns query from each table as separate
    # so need to loop through to put them together and return
    data = []
    for user, user_role in users:
        user_info = user.json()
        user_info["role_name"] = user_role.role_name
        data.append(user_info)
    return jsonify(
        {
            "code": 200,
            "data": data
        }
    ), 200
