from sqlalchemy import and_
from flask import jsonify, request
from app import app, db

from user import User
from course import Course
from enrol import Enrolment, addEnrolment
from group import Group


class EnrolmentRequest(db.Model):
    __tablename__ = 'enrolment_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.String(100), nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    course_enrolment_id = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'is_approved' : self.is_approved,
            'approved_by': self.approved_by,
            'course_enrolment_id': self.course_enrolment_id
        }

# view all enrolment request
@app.route("/enrolment_request",methods=["GET"])
def getAllRequests():
    #Query DB
    enrolment_requests = EnrolmentRequest.query.all()
    return jsonify(
        {
            "code" : 200,
            "data": [enrolment_request.json() for enrolment_request in enrolment_requests]
        }
    ), 200

#Add Request
@app.route("/enrolment_request",methods=["POST"])
def addRequest(data):
    if not data:
        data = request.get_json()
    try:
        # if add enrolment success then add to DB
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
        enrolment_request = EnrolmentRequest(
            user_id = data['user_id'],
            group_id = data['group_id'],
            course_enrolment_id = data['course_enrolment_id']
        )
        db.session.add(enrolment_request)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Successfully created an enrolment request"
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while creating request: {e}"
            }
        )



'''
Sample Request Body
{
    "approved_by":1,

}
'''
# Approve requests 
@app.route("/enrolment_request/approve/<int:id>", methods=["PUT"])
def approveRequest(id):
    data = request.get_json()
    enrolment_request = EnrolmentRequest.query.filter_by(request_id=id).first()
    if enrolment_request:
        try:
            user = User.query.filter_by(id=data['approved_by']).first()
            if user:
                enrolment_request.is_approved=1
                enrolment_request.approved_by=user.id
                db.session.commit()
                user_id = enrolment_request.user_id
                group_id = enrolment_request.group_id
                data['user_id']= user_id
                data['group_id']=group_id
                addEnrolment(data)
                return jsonify(
                    {
                        "code": 200,
                        "message": "Enrolment Request Successfully Approved"
                    }
                )
        except Exception as e:
            return jsonify(
                {
                    "code":500,
                    "message": f"An error occurred while approving request: {e}"
                }
            )
    else:
        return jsonify(
            {
                "code":404,
                "message": f"Invalid Enrolment Request ${id}"
            }
        )


