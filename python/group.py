from datetime import datetime

from flask import jsonify, request
from sqlalchemy import and_

from app import app, db
from course import Course
from user import User
from datetime import datetime


class Group(db.Model):

    __tablename__ = 'group'
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
    group_id = db.Column(db.Integer, primary_key=True, nullable=False)
    assigned_dt = db.Column(db.DateTime, nullable=False)
    assigned_end_dt = db.Column(db.DateTime, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'trainer_id': self.trainer_id,
            'assigned_dt': self.assigned_dt
        }

# Get all group
@app.route("/all_group/<int:id>", methods=['GET'])
def getAllGroups(id):
    groups = db.session.query(Group, TrainerAssignment, User, Course).filter(Group.course_id==id)\
            .outerjoin(TrainerAssignment, 
                and_(
                    Group.id == TrainerAssignment.group_id,
                    TrainerAssignment.assigned_end_dt == None))\
            .outerjoin(User, TrainerAssignment.trainer_id == User.id)\
            .outerjoin(Course, Group.course_id == Course.id).all()
    data = []
    for group, trainer_assignment, user, course in groups:
        group = group.json()
        group['course_name'] = course.name
        group['trainer_name'] = user.name
        data.append(group)
    return jsonify(
        {
            "code": 200,
            "data": data
        }
    ), 200

# Get one group
@app.route("/group/<int:id>", methods=['GET'])
def getOneGroup(id):
    group, trainer_assignment, user, course = db.session.query(Group, TrainerAssignment, User, Course).filter_by(id=id)\
        .outerjoin(TrainerAssignment, 
            and_(
                Group.id == TrainerAssignment.group_id,
                TrainerAssignment.assigned_end_dt == None))\
        .outerjoin(User, TrainerAssignment.trainer_id == User.id)\
        .outerjoin(Course, Group.course_id == Course.id).first()
    if group:
        group = group.json()
        group['course_name'] = course.name
        group['trainer_name'] = user.name
        return jsonify(
            {
                "code": 200,
                "data": group
            }
        ), 200
    else:
        return jsonify(
            {
                "code":404,
                "data": {
                    "id": id
                },
                "message": "Group not found."
            }
        )

# Add one group
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
@app.route("/group", methods=['POST'])
def addGroup():
    data = request.get_json()
    group = Group(
        course_id = data['course_id'],
        start_date = data['start_date'],
        end_date = data['end_date'],
        size = data['size']
    )
    try:
        db.session.add(group)
        db.session.commit()
        trainer_assignment = TrainerAssignment(
                                    trainer_id = data['trainer_id'], 
                                    group_id = group.id,
                                    assigned_dt = datetime.now())
        db.session.add(trainer_assignment)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while adding groups: {e}"
            }
        )
    
    return jsonify(
        {
            "code": 200,
            "data": group.json()
        }
    ), 200

#  Update Group
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
@app.route("/group", methods=['PUT'])
def updateGroup():
    try:
        data = request.get_json()
        id = data['id']
        group = Group.query.filter_by(id=id).first()
        if not group:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Group not found."
                }
            )
        group.course_id = data['course_id']
        group.start_date = data['start_date']
        group.end_date = data['end_date']
        group.size = data['size']

        assignment = TrainerAssignment.query.filter(TrainerAssignment.group_id == id, TrainerAssignment.assigned_end_dt == None).first()
        if data['trainer_id'] != assignment.json()['trainer_id']:
            assignment.assigned_end_dt = datetime.now()
            new_assignment = TrainerAssignment(
                                    trainer_id = data['trainer_id'], 
                                    group_id = group.id,
                                    assigned_dt = datetime.now())
            db.session.add(new_assignment)
        db.session.commit()
        
        return jsonify(
            {
                "code": 200,
                "data": data,
                "message": "Group successfully updated"
            }
        )

    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while updating group: {e}"
            }
        )

# Delete group
@app.route("/group/<int:id>", methods=['DELETE'])
def deleteGroup(id):
    group = Group.query.filter_by(id=id).first()
    if not group:
        return jsonify(
            {
                "code":404,
                "data": {
                    "id": id
                },
                "message": "Group not found."
            }
        )
    try:
        trainer_assignment = TrainerAssignment.query.filter(TrainerAssignment.group_id==id).all()
        if trainer_assignment:
            for assignment in trainer_assignment:
                db.session.delete(assignment)
            db.session.commit()
        db.session.delete(group)
        db.session.commit()
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while deleting group: {e}"
            }
        )
    return jsonify(
        {
            "code": 200,
            "message": "Group successfully deleted"
        }
    )
