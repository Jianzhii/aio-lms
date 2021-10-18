from types import prepare_class
from app import app, db
from flask import json, jsonify, request
from user import User
from datetime import datetime

class Course(db.Model):

    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prerequisite = db.Column(db.JSON, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prerequisite': self.prerequisite
        }

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'name': self.name
        }

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id =  db.Column(db.Integer, nullable=False)
    badges_id =  db.Column(db.Integer, nullable=False)
    assigned_dt= db.Column(db.DateTime, nullable=False)

    def json(self):
        return {
            'id':self.id,
            'user_id': self.user_id,
            'badges_id': self.badges_id,
            'assigned_dt': self.assigned_dt
        }

# Get all Courses
@app.route("/all_course", methods=['GET'])
def getAllCourse():
    courses = Course.query.all()
    data = []
    for course in courses: 
        course = course.json()
        if course['prerequisite']:
            prequisites = []
            for prerequisite in course['prerequisite']:
                prerequisite_course = Course.query.filter_by(id=prerequisite).first()
                prequisites.append(prerequisite_course.name)
            course['prerequisite'] = ",<br>".join(prequisites)
        else:
            course['prerequisite'] = "-"
        data.append(course)
    return jsonify(
        {
            "code": 200,
            "data": data
        }
    ), 200

@app.route("/search_course", methods=["POST"])
def searchCourse():
    data = request.get_json()
    try:
        courses = Course.query.filter(
                    Course.name.like(f"%{data['search']}%"),
                    Course.name.like(f"%{data['search']}%")
                ).all()
        data = []
        for course in courses: 
            course = course.json()
            if course['prerequisite']:
                prequisites = []
                for prerequisite in course['prerequisite']:
                    prerequisite_course = Course.query.filter_by(id=prerequisite).first()
                    prequisites.append(prerequisite_course.name)
                course['prerequisite'] = ",<br>".join(prequisites)
            else:
                course['prerequisite'] = "-"
            data.append(course)
        if courses: 
            return jsonify(
                {
                    "code": 200,
                    "data": data
                }
            ), 200
        else:
            return jsonify(
                {
                    "code": 200,
                    "data": []
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code":404,
                "message": f"Error while searching: {e}."
            }
        ), 404

# Get one course
@app.route("/course/<int:id>", methods=['GET'])
def getoneCourse(id):
    course = Course.query.filter_by(id=id).first()
    if course:
        course = course.json()
        if course['prerequisite']:
            prequisites = []
            for prerequisite in course['prerequisite']:
                prerequisite_course = Course.query.filter_by(id=prerequisite).first()
                prequisites.append(prerequisite_course.name)
            course['prerequisite'] = ",<br>".join(prequisites)
        else:
            course['prerequisite'] = "-"
        return jsonify(
            {
                "code": 200,
                "data": course
            }
        ), 200
    else:
        return jsonify(
            {
                "code":404,
                "data": {
                    "id": id
                },
                "message": "Course not found."
            }
        ), 404

# Add one course
'''
sample request
{
    "name": "Engineering",
    "description": "asdfasdsahdoashdioasdhoiashdoisahdoiashdosahdioh",
    "prerequisite": [1, 2]
}
'''
@app.route("/course", methods=['POST'])
def addCourse():
    data = request.get_json()
    try:
        course = Course(**data)
        db.session.add(course)
        db.session.commit()
        badge = Badge(
            course_id = course.id,
            name = course.name
        )
        db.session.add(badge)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Course successfully created!",
                "data": course.json()
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while creating course: {e}"
            }
        ), 500

#  Update Course
'''
sample request
{
    "id": 1,
    "name": "Engineering",
    "description": "asdfasdsahdoashdioasdhoiashdoisahdoiashdosahdioh",
    "prerequisite": [1, 2]
}
'''
@app.route("/course", methods=['PUT'])
def updateCourse():
    try:
        data = request.get_json()
        id = data['id']
        course = Course.query.filter_by(id=id).first()
        if not course:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Course not found."
                }
            ), 404
        course.name = data['name']
        course.description = data['description']
        course.prerequisite = data['prerequisite']
        db.session.commit()
        
        return jsonify(
            {
                "code": 200,
                "data": data,
                "message": "Course successfully updated"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while updating course: {e}"
            }
        ), 500

# Delete course
@app.route("/course/<int:id>", methods=['DELETE'])
def deleteCourse(id):
    try:
        from group import Group, TrainerAssignment
        from enrol import Enrolment
        course = Course.query.filter_by(id=id).first()
        badge = Badge.query.filter_by(course_id=id).first()
        ongoing_group = Group.query.filter(Group.course_id == course.id, Group.end_date >= datetime.now()).first()

        if ongoing_group:
            return jsonify(
                {
                    "code":500,
                    "data": {
                        "id": id
                    },
                    "message": f"{course.name} still have ongoing classes!"
                } 
            ), 500

        if not course:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Course not found."
                }
            ), 404
        all_groups = Group.query.filter(Group.course_id == course.id).all()

        if all_groups:
            for group in all_groups:
                assignment = TrainerAssignment.query.filter_by(group_id = group.id).all()
                if assignment:
                    db.session.execute(TrainerAssignment.__table__.delete().where(TrainerAssignment.group_id == group.id))

                enrolment = Enrolment.query.filter_by(group_id = group.id).all()
                if enrolment:
                    db.session.execute(Enrolment.__table__.delete().where(Enrolment.group_id == group.id))
                db.session.delete(group)
        db.session.delete(badge)
        db.session.delete(course)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Course successfully deleted"
            }
        )    
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while deleting course: {e}"
            }
        )

# View completed courses and Bages by user
@app.route("/course/completed/<int:id>", methods=["GET"])
def viewCompletedCourses(id):
    from enrol import Enrolment
    courses = db.session.query(UserBadge,Badge,Enrolment).filter(UserBadge.user_id==id)\
              .join(Badge, Badge.id == UserBadge.badges_id )\
              .join(Enrolment,Enrolment.user_id == UserBadge.user_id ).all()
    data = []
    for course,badge,enrolment in courses:
        course = course.json()
        course['course_name'] =badge.name
        course['group_id'] = enrolment.group_id
        data.append(course)
    return jsonify(
        {
            "code":200,
            "data" : data
        }
    ),200

