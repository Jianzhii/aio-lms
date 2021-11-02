from datetime import datetime

from flask import jsonify, request
from sqlalchemy import and_

from app import app, db
from course import Course, getTrainerAssignment
from user import User


class Group(db.Model):

    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    enrol_start_date = db.Column(db.DateTime, nullable=False)
    enrol_end_date = db.Column(db.DateTime, nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "start_date": self.start_date.strftime("%d/%m/%Y, %H:%M:%S"),
            "end_date": self.end_date.strftime("%d/%m/%Y, %H:%M:%S"),
            "enrol_start_date": self.enrol_start_date.strftime("%d/%m/%Y, %H:%M:%S"),
            "enrol_end_date": self.enrol_end_date.strftime("%d/%m/%Y, %H:%M:%S"),
            "size": self.size,
        }


class TrainerAssignment(db.Model):

    __tablename__ = "trainer_assignment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trainer_id = db.Column(db.Integer, primary_key=True, nullable=False)
    group_id = db.Column(db.Integer, primary_key=True, nullable=False)
    assigned_dt = db.Column(db.DateTime, nullable=False)
    assigned_end_dt = db.Column(db.DateTime, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "trainer_id": self.trainer_id,
            "assigned_dt": self.assigned_dt,
        }


# Get all group
@app.route("/all_group/<int:id>", methods=["GET"])
def getAllGroups(id):
    try:
        groups = (
            db.session.query(Group, TrainerAssignment, User, Course)
            .filter(Group.course_id == id, Group.end_date > datetime.now())
            .outerjoin(
                TrainerAssignment,
                and_(
                    Group.id == TrainerAssignment.group_id,
                    TrainerAssignment.assigned_end_dt == None,
                ),
            )
            .outerjoin(User, TrainerAssignment.trainer_id == User.id)
            .outerjoin(Course, Group.course_id == Course.id)
            .all()
        )
        data = []
        for group, trainer_assignment, user, course in groups:
            group = group.json()
            group["course_name"] = course.name
            group["trainer_name"] = user.name
            data.append(group)
        return jsonify(
            {
                "code": 200,
                "message": "Successfully retrieved all groups",
                "data": data
            }
        ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while retrieving group: {e}",
                }
            ), 406


# Get one group
@app.route("/group/<int:id>", methods=["GET"])
def getOneGroup(id):
    try:
        group, trainer_assignment, user, course = (
            db.session.query(Group, TrainerAssignment, User, Course)
            .filter_by(id=id)
            .outerjoin(
                TrainerAssignment,
                and_(
                    Group.id == TrainerAssignment.group_id,
                    TrainerAssignment.assigned_end_dt == None,
                ),
            )
            .outerjoin(User, TrainerAssignment.trainer_id == User.id)
            .outerjoin(Course, Group.course_id == Course.id)
            .first()
        )
        if group:
            group = group.json()
            group["course_name"] = course.name
            group["trainer_name"] = user.name
            return jsonify(
                {
                    "code": 200,
                    "message": "Successfully retrieved group.",
                    "data": group
                }
            ), 200
        else:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Group not found."
                    }
                ), 406
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while retrieving group: {e}",
                }
            ), 406


# Add one group
"""
sample request
{
    "course_id": 1,
    "size": 60,
    "start_date": "2021-10-15 12:00:00",
    "end_date": "2021-12-15 23:59:59",
    "enrol_start_date": "2021-09-15 12:00:00",
    "enrol_end_date": "2021-10-15 23:59:59",
    "trainer_id": 1
}
"""
@app.route("/group", methods=["POST"])
def addGroup():
    data = request.get_json()
    try:
        if data["start_date"] > data["end_date"]:
            e = Exception("End date cannot be before start date!")
            raise e

        if data["enrol_start_date"] > data["enrol_end_date"]:
            e = Exception("Enrolment end start cannot be before enrolment start date!")
            raise e

        if data["enrol_end_date"] > data["start_date"]:
            e = Exception("Enrolment period cannot end after group started!")
            raise e

        if not data["size"]:
            e = Exception("Please input group size!")
            raise e
        if not data["trainer_id"]:
            e = Exception("Please select a trainer!")
            raise e

        group = Group(
            course_id=data["course_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            enrol_start_date=data["enrol_start_date"],
            enrol_end_date=data["enrol_end_date"],
            size=data["size"],
        )
        db.session.add(group)
        db.session.commit()
        trainer_assignment = TrainerAssignment(
            trainer_id=data["trainer_id"], group_id=group.id, assigned_dt=datetime.now()
        )
        db.session.add(trainer_assignment)
        db.session.commit()

        return jsonify(
                {
                    "code": 200,
                    "message": "Group successfully created! ",
                    "data": group.json(),
                }
            ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while adding groups: {e}"
                }
            ), 406


#  Update Group
"""
sample request
{
    "id": 3,
    "course_id": 1,
    "size": 60,
    "start_date": "2021-10-15 12:00:00",
    "end_date": "2021-12-15 23:59:59",
    "enrol_start_date": "2021-09-15 12:00:00",
    "enrol_end_date": "2021-10-15 23:59:59",
    "trainer_id": 1
}
"""
@app.route("/group", methods=["PUT"])
def updateGroup():
    try:
        data = request.get_json()
        id = data["id"]
        group = Group.query.filter_by(id=id).first()
        if not group:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Group not found."
                    }
            ), 406
        group.course_id = data["course_id"]
        group.start_date = data["start_date"]
        group.end_date = data["end_date"]
        group.size = data["size"]
        group.enrol_start_date = data["enrol_start_date"]
        group.enrol_end_date = data["enrol_end_date"]

        assignment = TrainerAssignment.query.filter(
            TrainerAssignment.group_id == id, TrainerAssignment.assigned_end_dt == None
        ).first()
        if data["trainer_id"] != assignment.json()["trainer_id"]:
            assignment.assigned_end_dt = datetime.now()
            new_assignment = TrainerAssignment(
                trainer_id=data["trainer_id"],
                group_id=group.id,
                assigned_dt=datetime.now(),
            )
            db.session.add(new_assignment)
        db.session.commit()

        return jsonify(
                {
                    "code": 200,
                    "data": data,
                    "message": "Group successfully updated"
                }
            ), 200

    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while updating group: {e}"
                }
            ), 406


# Delete group
@app.route("/group/<int:id>", methods=["DELETE"])
def deleteGroup(id):
    try:
        from enrol import Enrolment
        from enrolment_request import EnrolmentRequest

        group = Group.query.filter_by(id=id).first()
        if not group:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Group not found."
                    }
                ), 406
        trainer_assignment = TrainerAssignment.query.filter(
            TrainerAssignment.group_id == id
        ).all()
        if trainer_assignment:
            for assignment in trainer_assignment:
                db.session.delete(assignment)

        all_enrolment_request = EnrolmentRequest.query.filter_by(group_id=id).all()
        if all_enrolment_request:
            for requests in all_enrolment_request:
                db.session.delete(requests)

        all_enrolment = Enrolment.query.filter_by(group_id=id).all()
        if all_enrolment:
            for enrolment in all_enrolment:
                db.session.delete(enrolment)

        db.session.commit()
        db.session.delete(group)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Group successfully deleted"
            }
        ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting group: {e}"
                }
            ), 406

# Get groups assigned to trainer in a course
@app.route("/group/trainer/<int:trainer_id>/<int:course_id>", methods=["GET"])
def groupsAssignedToTrainer(trainer_id, course_id):
    try:
        assignments = getTrainerAssignment(trainer_id)
        if assignments:
            data = []
            for assignment in assignments:
                if assignment["course_id"] == course_id:
                    data.append(assignment)
            return jsonify(
                    {
                        "code": 200,
                        "message": "Successfully retrieved courses",
                        "data": data,
                    }
                ), 200
        else:
            return jsonify(
                    {
                        "code": 200,
                        "message": "Successfully retrieved courses",
                        "data": [],
                    }
                ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while retrieving groups: {e}",
                }
            ), 406
