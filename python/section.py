from datetime import datetime

from flask import jsonify, request
from sqlalchemy import and_
from sqlalchemy.sql.expression import null

from app import app, db
from course import Course
from user import User


class Section(db.Model):

    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, primary_key=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'size': self.size
        }

class TrainerAssignment(db.Model):

    __tablename__ = 'trainer_assignment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trainer_id = db.Column(db.Integer, primary_key=True, nullable=False)
    section_id = db.Column(db.Integer, primary_key=True, nullable=False)
    assigned_dt = db.Column(db.DateTime, nullable=False)
    assigned_end_dt = db.Column(db.DateTime, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'trainer_id': self.trainer_id,
            'assigned_dt': self.assigned_dt
        }

# Get all Section
@app.route("/all_section", methods=['GET'])
def getAllSections():
    sections = db.session.query(Section, TrainerAssignment, User, Course)\
            .outerjoin(TrainerAssignment, 
                and_(
                    Section.id == TrainerAssignment.section_id,
                    TrainerAssignment.assigned_end_dt == None))\
            .outerjoin(User, TrainerAssignment.trainer_id == User.id)\
            .outerjoin(Course, Section.course_id == Course.id).all()
    data = []
    for section, trainer_assignment, user, course in sections:
        section = section.json()
        section['course_name'] = course.name
        section['trainer_name'] = user.name
        data.append(section)
    return jsonify(
        {
            "code": 200,
            "data": data
        }
    ), 200

# Get one section
@app.route("/section/<int:id>", methods=['GET'])
def getOneSection(id):
    section, trainer_assignment, user, course = db.session.query(Section, TrainerAssignment, User, Course).filter_by(id=id)\
        .outerjoin(TrainerAssignment, 
            and_(
                Section.id == TrainerAssignment.section_id,
                TrainerAssignment.assigned_end_dt == None))\
        .outerjoin(User, TrainerAssignment.trainer_id == User.id)\
        .outerjoin(Course, Section.course_id == Course.id).first()
    print(section)
    if section:
        section = section.json()
        section['course_name'] = course.name
        section['trainer_name'] = user.name
        return jsonify(
            {
                "code": 200,
                "data": section
            }
        ), 200
    else:
        return jsonify(
            {
                "code":404,
                "data": {
                    "id": id
                },
                "message": "Section not found."
            }
        )

# Add one section
@app.route("/section", methods=['POST'])
def addSection():
    data = request.get_json()
    section = Section(
        course_id = data['course_id'],
        start_date = data['start_date'],
        end_date = data['end_date'],
        size = data['size']
    )
    try:
        db.session.add(section)
        db.session.commit()
        trainer_assignment = TrainerAssignment(
                                    trainer_id = data['trainer_id'], 
                                    section_id = section.id,
                                    assigned_dt = datetime.now())
        db.session.add(trainer_assignment)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while adding sections: {e}"
            }
        )
    
    return jsonify(
        {
            "code": 200,
            "data": section.json()
        }
    ), 200

#  Update Course TODO
@app.route("/course", methods=['PUT'])
def updatesection():
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
            )
        course.name = data['name']
        course.description = data['description']
        db.session.commit()
        
        return jsonify(
            {
                "code": 200,
                "data": data,
                "message": "Course successfully updated"
            }
        )

    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while updating course: {e}"
            }
        )

# Delete course TODO
@app.route("/course/<int:id>", methods=['DELETE'])
def deleteSection(id):
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
        )
    try:
        db.session.delete(course)
        db.session.commit()
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while deleting course: {e}"
            }
        )
    return jsonify(
        {
            "code": 200,
            "message": "Course successfully deleted"
        }
    )
