from datetime import datetime

from flask import jsonify, request
from sqlalchemy import and_
from sqlalchemy.sql.expression import null

from __main__ import app, db
from course import Course
from user import User
from datetime import datetime


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
            'start_date': self.start_date.strftime("%d/%m/%Y, %H:%M:%S"),
            'end_date': self.end_date.strftime("%d/%m/%Y, %H:%M:%S"),
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
@app.route("/all_section/<int:id>", methods=['GET'])
def getAllSections(id):
    sections = db.session.query(Section, TrainerAssignment, User, Course).filter(Section.course_id==id)\
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
'''
sample request
{
    "course_id": 1,
    "size": 60,
    "start_date": "2021-10-15 12:00:00",
    "end_date": "2021-12-15 23:59:59",
    "trainer_id": 1
}
'''
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

#  Update Section TODO
'''
sample request
{
    "id": 3,
    "course_id": 1,
    "size": 60,
    "start_date": "2021-10-15 12:00:00",
    "end_date": "2021-12-15 23:59:59",
    "trainer_id": 1
}
'''
@app.route("/section", methods=['PUT'])
def updatesection():
    try:
        data = request.get_json()
        id = data['id']
        section = Section.query.filter_by(id=id).first()
        if not section:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Section not found."
                }
            )
        section.course_id = data['course_id']
        section.start_date = data['start_date']
        section.end_date = data['end_date']
        section.size = data['size']

        assignment = TrainerAssignment.query.filter(TrainerAssignment.section_id == id, TrainerAssignment.assigned_end_dt == None).first()
        if data['trainer_id'] != assignment.json()['trainer_id']:
            assignment.assigned_end_dt = datetime.now()
            new_assignment = TrainerAssignment(
                                    trainer_id = data['trainer_id'], 
                                    section_id = section.id,
                                    assigned_dt = datetime.now())
            db.session.add(new_assignment)
        db.session.commit()
        
        return jsonify(
            {
                "code": 200,
                "data": data,
                "message": "Section successfully updated"
            }
        )

    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while updating section: {e}"
            }
        )

# Delete Section TODO
@app.route("/section/<int:id>", methods=['DELETE'])
def deleteSection(id):
    section = Section.query.filter_by(id=id).first()
    if not section:
        return jsonify(
            {
                "code":404,
                "data": {
                    "id": id
                },
                "message": "Section not found."
            }
        )
    try:
        trainer_assignment = TrainerAssignment.query.filter(TrainerAssignment.section_id==id).all()
        if trainer_assignment:
            for assignment in trainer_assignment:
                db.session.delete(assignment)
            db.session.commit()
        db.session.delete(section)
        db.session.commit()
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while deleting section: {e}"
            }
        )
    return jsonify(
        {
            "code": 200,
            "message": "Section successfully deleted"
        }
    )
