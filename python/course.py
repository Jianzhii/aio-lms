from datetime import datetime

from flask import jsonify, request
from sqlalchemy.sql.expression import and_

from app import app, db


class Course(db.Model):

    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prerequisite = db.Column(db.JSON, nullable=True)

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "prerequisite": self.prerequisite,
        }


class Badge(db.Model):
    __tablename__ = "badges"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "name": self.name
        }


class UserBadge(db.Model):
    __tablename__ = "user_badges"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    badges_id = db.Column(db.Integer, nullable=False)
    assigned_dt = db.Column(db.DateTime, nullable=True)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "badges_id": self.badges_id,
            "assigned_dt": self.assigned_dt,
        }


# Get all Courses
@app.route("/all_course", methods=["GET"])
def getAllCourse():
    courses = Course.query.all()
    data = []
    for course in courses:
        course = course.json()
        if course["prerequisite"]:
            prequisites = []
            for prerequisite in course["prerequisite"]:
                prerequisite_course = Course.query.filter_by(id=prerequisite).first()
                prequisites.append(prerequisite_course.name)
            course["prerequisite"] = ",<br>".join(prequisites)
        else:
            course["prerequisite"] = "-"
        data.append(course)
    return jsonify(
        {
            "code": 200,
            "message": "Courses successfully retrieved",
            "data": data
        }
    ), 200


# get course by search
@app.route("/search_course", methods=["POST"])
def searchCourse():
    data = request.get_json()
    try:
        courses = Course.query.filter(
            Course.name.like(f"%{data['search']}%"),
            Course.name.like(f"%{data['search']}%"),
        ).all()
        data = []
        for course in courses:
            course = course.json()
            if course["prerequisite"]:
                prequisites = []
                for prerequisite in course["prerequisite"]:
                    prerequisite_course = Course.query.filter_by(
                        id=prerequisite
                    ).first()
                    prequisites.append(prerequisite_course.name)
                course["prerequisite"] = ",<br>".join(prequisites)
            else:
                course["prerequisite"] = "-"
            data.append(course)
        if courses:
            return jsonify(
                {
                    "code": 200,
                    "message": "Courses successfully retrieved",
                    "data": data
                }
            ), 200
        else:
            return jsonify(
                {
                    "code": 200,
                    "message": "Courses successfully retrieved",
                    "data": []
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 406,
                "message": f"Error while searching: {e}."
            }
        ), 406


# Get one course
@app.route("/course/<int:id>", methods=["GET"])
def getoneCourse(id):
    course = Course.query.filter_by(id=id).first()
    if course:
        course = course.json()
        if course["prerequisite"]:
            prequisites = []
            for prerequisite in course["prerequisite"]:
                prerequisite_course = Course.query.filter_by(id=prerequisite).first()
                prequisites.append(prerequisite_course.name)
            course["prerequisite"] = ",<br>".join(prequisites)
        else:
            course["prerequisite"] = "-"
        return jsonify(
            {
                "code": 200,
                "message": "Course successfully retrieved",
                "data": course
            }
        ), 200
    else:
        db.session.rollback()
        return jsonify(
            {
                "code": 406,
                "data": {"id": id},
                "message": "Course not found."
            }
        ), 406


# Add one course
"""
sample request
{
    "name": "Engineering",
    "description": "asdfasdsahdoashdioasdhoiashdoisahdoiashdosahdioh",
    "prerequisite": [1, 2]
}
"""
@app.route("/course", methods=["POST"])
def addCourse():
    data = request.get_json()
    try:
        course = Course(**data)
        db.session.add(course)
        db.session.commit()
        badge = Badge(course_id=course.id, name=course.name)
        db.session.add(badge)
        db.session.commit()

        return jsonify(
                {
                    "code": 200,
                    "message": "Course successfully created!",
                    "data": course.json()
                }
            ), 200,
    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while creating course: {e}",
                }
            ), 406


#  Update Course
"""
sample request
{
    "id": 1,
    "name": "Engineering",
    "description": "asdfasdsahdoashdioasdhoiashdoisahdoiashdosahdioh",
    "prerequisite": [1, 2]
}
"""
@app.route("/course", methods=["PUT"])
def updateCourse():
    try:
        data = request.get_json()
        id = data["id"]
        course = Course.query.filter_by(id=id).first()
        if not course:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Course not found."
                    }
                ), 406
        course.name = data["name"]
        course.description = data["description"]
        course.prerequisite = data["prerequisite"]
        db.session.commit()

        return jsonify(
                {
                    "code": 200,
                    "data": data,
                    "message": "Course successfully updated"
                }
            ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while updating course: {e}"
                }
            ), 406


# Delete course
@app.route("/course/<int:id>", methods=["DELETE"])
def deleteCourse(id):
    try:
        from enrol import Enrolment
        from group import Group, TrainerAssignment
        from enrolment_request import EnrolmentRequest
        from section_progress import SectionProgress

        course = Course.query.filter_by(id=id).first()
        badge = Badge.query.filter_by(course_id=id).first()
        ongoing_group = Group.query.filter(
            Group.course_id == course.id, Group.end_date >= datetime.now()
        ).first()

        if ongoing_group:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": f"{course.name} still have ongoing classes!"
                    }
            ), 406

        if not course:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Course not found."
                    }
                ), 406
        all_groups = Group.query.filter(Group.course_id == course.id).all()

        if all_groups:
            for group in all_groups:
                assignment = TrainerAssignment.query.filter_by(group_id=group.id).all()
                if assignment:
                    db.session.execute(
                        TrainerAssignment.__table__.delete().where(
                            TrainerAssignment.group_id == group.id
                        )
                    )

                enrolments = Enrolment.query.filter_by(group_id=group.id).all()
                if enrolments:
                    for enrolment in enrolments: 
                        db.session.execute(
                            EnrolmentRequest.__table__.delete().where(
                                EnrolmentRequest.course_enrolment_id == enrolment.id
                            )
                        )
                        db.session.execute(
                            SectionProgress.__table__.delete().where(
                                SectionProgress.grocourse_enrolment_idup_id == enrolment.id
                            )
                        )
                    db.session.execute(
                        Enrolment.__table__.delete().where(
                            Enrolment.group_id == group.id
                        )
                    )
                db.session.delete(group)
        db.session.delete(badge)
        db.session.delete(course)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Course successfully deleted"
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 406,
                "message": f"An error occurred while deleting course: {e}"
            }
        ), 406


# View completed courses and Badges by user
@app.route("/course/badges/<int:id>", methods=["GET"])
def viewCompletedCourses(id):
    from enrol import Enrolment

    courses = (
        db.session.query(UserBadge, Badge, Enrolment)
        .filter(UserBadge.user_id == id)
        .join(Badge, Badge.id == UserBadge.badges_id)
        .join(Enrolment, Enrolment.user_id == UserBadge.user_id)
        .all()
    )
    data = []
    for course, badge, enrolment in courses:
        course = course.json()
        course["course_name"] = badge.name
        course["group_id"] = enrolment.group_id
        data.append(course)
    return jsonify(
        {
            "code": 200,
            "message": "Enrolment successfully retrieved.",
            "data": data
        }
    ), 200


# Get distinct courses assigned to trainer
@app.route("/course/trainer/<int:trainer_id>", methods=["GET"])
def courseAssignedToTrainer(trainer_id):
    try:
        assignment = getTrainerAssignment(trainer_id)
        if assignment:
            data = []
            for each in assignment:
                info = {
                    "course_id": each["course_id"],
                    "course_name": each["course_name"],
                }
                if info not in data:
                    data.append(info)
            return jsonify(
                    {
                        "code": 200,
                        "message": "Successfully retrieved courses",
                        "data": data
                    }
                ), 200
        else:
            return jsonify(
                    {
                        "code": 200,
                        "message": "Successfully retrieved courses",
                        "data": []
                    }
                ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 406,
                "message": f"Error while retrieving courses: {e}."
            }
        ), 406


def getTrainerAssignment(trainer_id):
    try:
        from group import Group, TrainerAssignment

        courses = (
            db.session.query(TrainerAssignment, Group, Course)
            .filter(
                and_(
                    TrainerAssignment.trainer_id == trainer_id,
                    TrainerAssignment.assigned_end_dt == None,
                )
            )
            .outerjoin(Group, Group.id == TrainerAssignment.group_id)
            .outerjoin(Course, Course.id == Group.course_id)
            .order_by(Course.id.asc(), Group.id.asc())
            .all()
        )

        data = []
        for assignment, group, course in courses:
            assignment = assignment.json()
            assignment["course_name"] = course.name
            assignment["course_id"] = course.id
            data.append(assignment)
        return data
    except Exception as e:
        raise e
