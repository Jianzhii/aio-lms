from datetime import datetime

from flask import jsonify, request

from app import app, db
from course import Course
from enrol import addEnrolment, processEnrolmentEligibility
from group import Group
from user import User


class EnrolmentRequest(db.Model):
    __tablename__ = "enrolment_request"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, primary_key=True)
    is_approved = db.Column(db.String(100), nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    course_enrolment_id = db.Column(db.Integer, nullable=True)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "group_id": self.group_id,
            "is_approved": self.is_approved,
            "approved_by": self.approved_by,
            "course_enrolment_id": self.course_enrolment_id,
        }


# view all enrolment request
@app.route("/enrolment_request", methods=["GET"])
def getAllRequests():
    # Query DB
    enrolment_requests = (
        db.session.query(EnrolmentRequest, Group, User, Course)
        .join(Group, Group.id == EnrolmentRequest.group_id)
        .join(User, User.id == EnrolmentRequest.user_id)
        .join(Course, Course.id == Group.course_id)
        .all()
    )
    data = []
    for enrol_request, group, user, course in enrolment_requests:
        enrol_request = enrol_request.json()
        enrol_request["course_id"] = group.course_id
        enrol_request["course_name"] = course.name
        enrol_request["user_name"] = user.name
        data.append(enrol_request)
    return jsonify(
        {
            "code": 200,
            "data": data,
            "message": "Successfully retrieved all request"
        }
    ), 200


# for Learner to view his pending enrolment requests
@app.route("/enrolment_request/learner/<int:userid>", methods=["GET"])
def getRequests(userid):
    # Query DB
    user = User.query.filter_by(id=userid).first()
    if user:
        enrolment_requests = (
            db.session.query(EnrolmentRequest, Group, Course)
            .filter(EnrolmentRequest.user_id == userid)
            .join(Group, Group.id == EnrolmentRequest.group_id)
            .join(Course, Course.id == Group.course_id)
            .all()
        )
        data = []
        # response
        for enrol_request, group, course in enrolment_requests:
            enrol_request = enrol_request.json()
            enrol_request["course_id"] = course.id
            enrol_request["course_name"] = course.name
            enrol_request["course_description"] = course.description
            data.append(enrol_request)
        return jsonify(
            {
                "code": 200,
                "message": "Successfully retrieved request",
                "data": data
            }
        ), 200
    else:
        return jsonify(
            {
                "code": 406,
                "message": f"Invalid User ${id}"
            }
        ), 406


"""
Sample Request Body:
{
    "user_id" : 1,
    "group_id" : 1,
}
"""
# Add Request
@app.route("/enrolment_request", methods=["POST"])
def addRequest():
    data = request.get_json()
    try:
        # join enrolment, group and course check if they have pending request
        user = User.query.filter_by(id=data["user_id"]).first()
        group = Group.query.filter_by(id=data["group_id"]).first()
        course_info = Course.query.filter_by(id=group.course_id).first()
        all_groups_under_course = [
            each.id for each in Group.query.filter_by(course_id=course_info.id).all()
        ]
        pending_requests = [
            each.group_id
            for each in EnrolmentRequest.query.filter_by(
                user_id=data["user_id"], is_approved=None
            ).all()
        ]
        if len(list(set(all_groups_under_course) & set(pending_requests))):
            return jsonify(
                    {
                        "code": 406,
                        "data": data,
                        "message": f"{user.name} has submitted a request and it is pending"
                    }
                ), 406

        # Approval need to check whether it is within start_date and end date  of class
        data["start_date"] = datetime.now()
        enrolment_period = checkEnrolmentPeriod(data)
        if enrolment_period:
            return enrolment_period

        result = processEnrolmentEligibility(data)

        if result[1] != 200:
            return result

        enrolment_request = EnrolmentRequest(
            user_id=data["user_id"],
            group_id=data["group_id"],
        )
        db.session.add(enrolment_request)
        db.session.commit()
        return jsonify(
                {
                    "code": 200,
                    "message": "Successfully created an enrolment request",
                    "data": enrolment_request.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while creating request: {e}",
                }
            ), 406


def checkEnrolmentPeriod(data):
    group = Group.query.filter_by(id=data["group_id"]).first()
    enrol_start_date = group.enrol_start_date
    enrol_end_date = group.enrol_end_date
    enrol_datetime = data["start_date"]
    if not (enrol_datetime >= enrol_start_date and enrol_datetime <= enrol_end_date):
        return jsonify(
                {
                    "code": 406,
                    "message": f"Sorry you are not allowed to submit a request outside the enrolment period: {enrol_datetime}"
                }
            ), 406


"""
Sample Request Body
{
    "approved_by":1
}
"""
# Approve requests
@app.route("/enrolment_request/approve/<int:request_id>", methods=["PUT"])
def approveRequest(request_id):
    data = request.get_json()
    enrolment_request = EnrolmentRequest.query.filter_by(id=request_id).first()
    if enrolment_request:
        try:
            user = User.query.filter_by(id=data["approved_by"]).first()
            if user:
                enrolment_request.is_approved = 1
                enrolment_request.approved_by = user.id
                user_id = enrolment_request.user_id
                group_id = enrolment_request.group_id
                data["user_id"] = user_id
                data["group_id"] = group_id
                result = addEnrolment(data)
                enrolment_request.course_enrolment_id = result[0].get_json()["data"][
                    "id"
                ]
                db.session.commit()
                return jsonify(
                        {
                            "code": 200,
                            "message": "Enrolment Request Successfully Approved",
                        }
                    ), 200
        except Exception as e:
            return jsonify(
                    {
                        "code": 406,
                        "message": f"An error occurred while approving request: {e}",
                    }
                ), 406
    else:
        return jsonify(
                {
                    "code": 406,
                    "message": f"Invalid Enrolment Request ${id}"
                }
            ), 406


# Delete enrolment
@app.route("/enrolment_request/<int:id>", methods=["DELETE"])
def deleteEnrolmentRequest(id):
    try:
        enrolment_request = EnrolmentRequest.query.filter_by(id=id).first()
        if not enrolment_request:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Enrolment Request not found.",
                    }
                ), 406
        db.session.delete(enrolment_request)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Enrolment Request successfully deleted"
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 406,
                "message": f"An error occurred while deleting enrolment  request: {e}",
            }
        ), 406
