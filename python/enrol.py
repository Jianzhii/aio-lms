from datetime import datetime

from flask import jsonify, request

from app import app, db
from course import Course
from user import User
from group import Group
from datetime import datetime
from sqlalchemy import and_


class Enrolment(db.Model):

    __tablename__ = 'course_enrolment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    enrolled_dt = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'enrolled_dt': self.enrolled_dt.strftime("%d/%m/%Y, %H:%M:%S"),
            'completed': self.completed
        }



# Get enrolment within a group
@app.route("/enrolment/group/<int:group_id>", methods=['GET'])
def getEnrolmentByGroup(group_id):
    groups = db.session.query(Enrolment, Group, User, Course).filter(Enrolment.group_id==group_id)\
            .outerjoin(Group, Group.id == Enrolment.group_id)\
            .outerjoin(User, Enrolment.user_id == User.id)\
            .outerjoin(Course, Group.course_id == Course.id).all()
    data = []
    for enrolment, group, user, course in groups:
        enrolment = enrolment.json()
        enrolment['learner_name'] = user.name
        enrolment['course_name'] = course.name
        data.append(enrolment)
    return jsonify(
        {
            "code": 200,
            "data": data
        }
    ), 200

# Get enrolment by user_id
@app.route("/enrolment/user/<int:user_id>", methods=['GET'])
def getEnrolmentByUser(user_id):
    groups = db.session.query(Enrolment, Group, User, Course).filter(User.id == user_id)\
            .outerjoin(Group, Group.id == Enrolment.group_id)\
            .outerjoin(User, Enrolment.user_id == User.id)\
            .outerjoin(Course, Group.course_id == Course.id).all()
    data = []
    for enrolment, group, user, course in groups:
        enrolment = enrolment.json()
        enrolment['learner_name'] = user.name
        enrolment['course_name'] = course.name
        data.append(enrolment)
    return jsonify(
        {
            "code": 200,
            "data": data
        }
    ), 200

# Enrol learner
'''
sample request
{
    "user_id": 3,
    "group_id": 1,
}
# '''
@app.route("/enrolment", methods=['POST'])
def addEnrolment():
    data = request.get_json()
    try:
        existing_enrolment = Enrolment.query.filter_by(user_id = data['user_id'], group_id = data['group_id']).all()
        user = User.query.filter_by(id=data['user_id']).first()
        if existing_enrolment: 
            return jsonify(
                {
                    "code":406,
                    "data": data,
                    "message": f"{user.name} has already been enrolled in this course"
                }
            ), 406
        
        group = Group.query.filter_by(id=data['group_id']).first()
        current_group_size = Enrolment.query.filter_by(group_id = data['group_id']).count()
        if current_group_size == group.size:
            return jsonify(
                {
                    "code":406,
                    "data": data,
                    "message": "Group enrollment is already full."
                }
            ),406
        
        course_info = Course.query.filter_by(id=group.course_id).first()
        if course_info.prerequisite:
            completed_course = [ course.id for enrolment, group, course in db.session.query(Enrolment, Group, Course).filter_by(user_id=data['user_id'], completed=True)\
                                                                                    .outerjoin(Group, Group.id == Enrolment.group_id)\
                                                                                    .outerjoin(Course, Group.course_id == Course.id).all()]
            incomplete = []
            for each in course_info.prerequisite:
                if each not in completed_course:
                    prerequisite_course_info = Course.query.filter_by(id=each).first()
                    incomplete.append(prerequisite_course_info.name)
            if len(incomplete):
                return jsonify(
                    {
                        "code":406,
                        "data": data,
                        "message": f"{user.name} has yet to complete the following prerequisite course(s): {', '.join(incomplete)}"
                    }
                ),406

        enrol = Enrolment(
            group_id = data['group_id'],
            user_id = data['user_id'],
            enrolled_dt = datetime.now(),
            completed = False
        )
        db.session.add(enrol)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Successfully enrolled learner"
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while enrolling learner: {e}"
            }
        ), 500

# Delete enrolment
@app.route("/enrolment/<int:id>", methods=['DELETE'])
def deleteEnrolment(id):
    try:
        enrolment = Enrolment.query.filter_by(id=id).first()
        if not enrolment:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Enrolment details not found."
                }
            )
        db.session.delete(enrolment)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Enrolment successfully deleted"
            }
        ),200
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while deleting enrolment: {e}"
            }
        )