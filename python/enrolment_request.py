from sqlalchemy import and_
from flask import jsonify, request
from app import app, db

from user import User
from course import Course
from enrol import Enrolment, processEnrolmentEligibility, addEnrolment
from group import Group


class EnrolmentRequest(db.Model):
    __tablename__ = 'enrolment_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.String(100), nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    course_enrolment_id = db.Column(db.Integer, nullable=True)

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
    enrolment_requests = db.session.query(EnrolmentRequest,Group)\
                        .join(Group,Group.id == EnrolmentRequest.group_id).all()
    data=[]
    for enrol_request,group in enrolment_requests:
        enrol_request = enrol_request.json()
        enrol_request['course_id'] = group.course_id
        data.append(enrol_request)
    return jsonify(
        {
            "code" : 200,
            "data": data
        }
    ), 200



#for Learner to view his pending enrolment requests
@app.route("/enrolment_request/learner/<int:userid>",methods=["GET"])
def getRequests(userid):
    #Query DB
    user = User.query.filter_by(id=userid).first()
    if user:
        enrolment_requests = db.session.query( EnrolmentRequest,Group,Course).filter(EnrolmentRequest.user_id==userid)\
            .join(Group, Group.id == EnrolmentRequest.group_id)\
            .join(Course, Course.id == Group.course_id).all()
        data = []
        # response
        for enrol_request,group,course  in enrolment_requests:
            enrol_request =enrol_request.json()
            enrol_request['course_id'] =course.id
            enrol_request['course_name'] = course.name
            enrol_request['course_description'] = course.description
            data.append(enrol_request)
        return jsonify(
            {
                "code" : 200,
                "data": data
            }
        ), 200
    else:
        return jsonify(
            {
                "code":404,
                "message": f"Invalid User ${id}"
            }
        ),404




#Add Request
@app.route("/enrolment_request",methods=["POST"])
def addRequest():
    data= request.get_json()
    try:
        result = processEnrolmentEligibility(data)
        if result[1] != 200:
            return result

        enrolment_request = EnrolmentRequest(
            user_id = data['user_id'],
            group_id = data['group_id'],
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
        ), 500






'''
Sample Request Body
{
    "approved_by":1,
    "course_enrolment_id":1
}
'''
# Approve requests 
@app.route("/enrolment_request/approve/<int:request_id>", methods=["PUT"])
def approveRequest(request_id):
    data = request.get_json()
    enrolment_request = EnrolmentRequest.query.filter_by(id=request_id).first()
    if enrolment_request:
        try:
            user = User.query.filter_by(id=data['approved_by']).first()
            if user:
                enrolment_request.is_approved=1
                enrolment_request.course_enrolment_id = data['course_enrolment_id']
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
                ), 200
        except Exception as e:
            return jsonify(
                {
                    "code":500,
                    "message": f"An error occurred while approving request: {e}"
                }
            ), 500
    else:
        return jsonify(
            {
                "code":404,
                "message": f"Invalid Enrolment Request ${id}"
            }
        ),404


# Delete enrolment
@app.route("/enrolment_request/<int:id>", methods=['DELETE'])
def deleteEnrolmentRequest(id):
    try:
        enrolment_request= EnrolmentRequest.query.filter_by(id=id).first()
        if not enrolment_request:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Enrolment Request not found."
                }
            ),404
        db.session.delete(enrolment_request)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Enrolment Request successfully deleted"
            }
        ),200
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while deleting enrolment  request: {e}"
            }
        )






