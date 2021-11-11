from datetime import datetime
from operator import ixor

from flask import jsonify, request

from app import app, db
from course import Course, Badge, UserBadge
from group import Group
from section_progress import SectionProgress, createProgressRecord
from user import User


class Enrolment(db.Model):
    __tablename__ = "course_enrolment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    enrolled_dt = db.Column(db.DateTime, nullable=True)
    is_quiz_pass = db.Column(db.Boolean, nullable=True)
    completed = db.Column(db.Boolean, nullable=True)

    def json(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "user_id": self.user_id,
            "enrolled_dt": self.enrolled_dt.strftime("%d/%m/%Y, %H:%M:%S"),
            "is_quiz_pass": self.is_quiz_pass,
            "completed": self.completed,
        }


# Get enrolment within a group
@app.route("/enrolment/group/<int:group_id>", methods=["GET"])
def getEnrolmentByGroup(group_id):
    groups = (
        db.session.query(Enrolment, Group, User, Course)
        .filter(Enrolment.group_id == group_id)
        .outerjoin(Group, Group.id == Enrolment.group_id)
        .outerjoin(User, Enrolment.user_id == User.id)
        .outerjoin(Course, Group.course_id == Course.id)
        .all()
    )
    data = []
    for enrolment, group, user, course in groups:
        enrolment = enrolment.json()
        enrolment["learner_name"] = user.name
        enrolment["course_name"] = course.name
        all_section_progress = SectionProgress.query.filter_by(
            course_enrolment_id=enrolment["id"]
        ).all()
        total_materials = 1
        total_completed = 0
        for section_progress in all_section_progress:
            total_materials += 1
            if section_progress.quiz_attempt:
                total_completed += 1
            for material in section_progress.material:
                total_materials += 1
                if section_progress.material[material]:
                    total_completed += 1
            # TODO to add in check for final quiz??
        if total_materials and total_completed:
            enrolment["completion_status"] = round(total_completed / total_materials, 2)
        else:
            enrolment["completion_status"] = 0
        if enrolment['is_quiz_pass']:
            total_completed += 1
        data.append(enrolment)
    return jsonify(
        {
            "code": 200,
            "message": "Successfully retrieved enrolment",
            "data": data
        }
    ), 200


# Get ongoing/ upcoming enrolment by user_id
@app.route("/enrolment/user/ongoing/<int:user_id>", methods=["GET"])
def getOngoingEnrolmentByUser(user_id):
    data = getEnrolment(user_id, False)
    return jsonify(
        {
            "code": 200,
            "message": "Successfully retrieved upcoming/ ongoing enrolment",
            "data": data
        }
    ), 200

# Get completed enrolment by user_id
@app.route("/enrolment/user/completed/<int:user_id>", methods=['GET'])
def getCompletedEnrolmentByUser(user_id):
    data = getEnrolment(user_id, True)
    return jsonify(
        {
            "code": 200,
            "message": "Successfully retrieved completed enrolment",
            "data": data
        }
    ), 200


def getEnrolment(user_id, status):
    groups = (
        db.session.query(Enrolment, Group, User, Course)
        .filter(User.id == user_id, Enrolment.completed == status)
        .outerjoin(Group, Group.id == Enrolment.group_id)
        .outerjoin(User, Enrolment.user_id == User.id)
        .outerjoin(Course, Group.course_id == Course.id)
        .all()
    )
    data = []
    for enrolment, group, user, course in groups:
        enrolment = enrolment.json()
        enrolment["learner_name"] = user.name
        enrolment["course_name"] = course.name
        enrolment["course_id"] = course.id
        data.append(enrolment)
    return data


# Enrol learner
"""
sample request
{
    "user_id": 3,
    "group_id": 1
}
will have to update course request... so everything
"""
@app.route("/enrolment", methods=["POST"])
def addEnrolment(data=None):
    if not data:
        data = request.get_json()
    result = None
    update = False
    if 'update' in data and data['update']:
        update = True
    try:
        if type(data["user_id"]) == list:
            for user in data["user_id"]:
                result = processEnrolmentEligibility(
                    {"user_id": user, "group_id": data["group_id"]}
                )
                if result[1] == 200:
                    db.session.add(result[0])
                    db.session.commit()
                    createProgressRecord(result[0].json())
                elif not update:
                    return result
                elif update and result[1] != 407:
                    return result
        else:
            result = processEnrolmentEligibility(data)
            if result[1] != 200:
                return result
            else:
                db.session.add(result[0])
                db.session.commit()
                createProgressRecord(result[0].json())

        db.session.commit()
        if update and result[1] == 407:
            return jsonify(
                {
                    "code": 200,
                    "data": {},
                    "message": "Learner has already been enrolled."
                }
            ), 200
        return jsonify(
                {
                    "code": 200,
                    "data": result[0].json() if result else {},
                    "message": "Successfully enrolled learners"
                }
        ), 200
    except Exception as e:
        enrolment = Enrolment.query.filter_by(id=result[0].json()["id"]).first()
        db.session.delete(enrolment)
        db.session.commit()
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while enrolling learner: {e}"
                }
            ), 406


def processEnrolmentEligibility(data):
    try:
        # check if learner alr enrolled in group
        existing_enrolment = Enrolment.query.filter_by(
            user_id=data["user_id"], group_id=data["group_id"]
        ).all()
        user = User.query.filter_by(id=data["user_id"]).first()
        if existing_enrolment:
            return jsonify(
                    {
                        "code": 407,
                        "data": data,
                        "message": f"{user.name} has already been enrolled in this group"
                    }
                ), 407

        # check if learner has alr completed course
        group = Group.query.filter_by(id=data["group_id"]).first()
        course_info = Course.query.filter_by(id=group.course_id).first()
        all_groups_under_course = [
            each.id for each in Group.query.filter_by(course_id=course_info.id).all()
        ]
        user_enrolment = [
            each.group_id
            for each in Enrolment.query.filter_by(
                user_id=data["user_id"], completed=True
            ).all()
        ]
        if len(list(set(all_groups_under_course) & set(user_enrolment))):
            return jsonify(
                    {
                        "code": 406,
                        "data": data,
                        "message": f"{user.name} has already been completed in this course"
                    }
                ), 406

        # check if learner is alr enrolled in upcoming or ongoing group under same course
        ongoing_groups_under_course = [
            each.id
            for each in Group.query.filter(
                Group.course_id == course_info.id, Group.end_date >= datetime.now()
            ).all()
        ]
        incompleted_user_enrolment = [
            each.group_id
            for each in Enrolment.query.filter_by(
                user_id=data["user_id"], completed=False
            ).all()
        ]
        if len(
            list(set(ongoing_groups_under_course) & set(incompleted_user_enrolment))
        ):
            return jsonify(
                    {
                        "code": 406,
                        "data": data,
                        "message": f"{user.name} has already been enrolled in an ongoing or upcoming group for this course"
                    }
                ), 406

        # check if group size can accommodate learner
        current_group_size = Enrolment.query.filter_by(
            group_id=data["group_id"]
        ).count()
        if current_group_size == group.size:
            return jsonify(
                    {
                        "code": 406,
                        "data": data,
                        "message": "Group enrollment is already full."
                    }
                ), 406

        # check if learner has alr fulfilled prerequisite
        if course_info.prerequisite:
            completed_course = [
                int(course.id)
                for enrolment, group, course in db.session.query(
                    Enrolment, Group, Course
                )
                .filter_by(user_id=data["user_id"], completed=True)
                .outerjoin(Group, Group.id == Enrolment.group_id)
                .outerjoin(Course, Group.course_id == Course.id)
                .all()
            ]
            incomplete = []
            for each in course_info.prerequisite:
                if int(each) not in completed_course:
                    prerequisite_course_info = Course.query.filter_by(id=each).first()
                    incomplete.append(prerequisite_course_info.name)
            if len(incomplete):
                return jsonify(
                        {
                            "code": 406,
                            "data": data,
                            "message": f"{user.name} has yet to complete the following prerequisite course(s): {', '.join(incomplete)}"
                        }
                    ), 406
        enrol = Enrolment(
            group_id=data["group_id"],
            user_id=data["user_id"],
            enrolled_dt=datetime.now(),
            completed=False,
            is_quiz_pass=False
        )
        return (enrol, 200)
    except Exception as e:
        db.session.rollback()
        raise e


# Delete enrolment
@app.route("/enrolment/<int:id>", methods=["DELETE"])
def deleteEnrolment(id):
    try:
        enrolment = Enrolment.query.filter_by(id=id).first()
        all_progress = SectionProgress.query.filter_by(course_enrolment_id=id).all()
        for progress in all_progress:
            db.session.delete(progress)
        db.session.commit()
        if not enrolment:
            return jsonify(
                {
                    "code": 406,
                    "data": {"id": id},
                    "message": "Enrolment details not found."
                }
            ), 406
        db.session.delete(enrolment)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Enrolment successfully deleted"
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting enrolment: {e}"
                }
            ), 406

def checkCompletionOfMaterial(enrol_id):
    try:
        section_progress = SectionProgress.query.filter_by(course_enrolment_id = enrol_id).all()
        for i in range(len(section_progress)):
            section = section_progress[i]
            for material in section.material:
                if not section.material[material]:
                    return False
            if not section.quiz_attempt:
                return False
        return True
    except Exception as e:
        raise e

def checkCompletionOfCourse(enrol_id):
    try:
        if not checkCompletionOfMaterial(enrol_id):
            return False
        enrolment = Enrolment.query.filter_by(id = enrol_id).first()
        if not enrolment.is_quiz_pass:
            return False
        enrolment.completed = True
        db.session.commit()
        assignBadges(enrolment.user_id, enrolment.group_id)

        return True
    except Exception as e:
        raise e

def assignBadges(user_id, group_id):
    try:
        group = Group.query.filter_by(id = group_id).first()
        course_id = group.course_id
        badge = Badge.query.filter_by(course_id = course_id).first()
        badge_assignment = UserBadge(
            user_id = user_id,
            badges_id = badge.id,
            assigned_dt = datetime.now()
        )
        db.session.add(badge_assignment)
        db.session.commit()
    except Exception as e:
        raise e
