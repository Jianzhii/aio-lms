from app import app, db
from flask import jsonify, request
from user import User

class Course(db.Model):

    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# Get all Courses
@app.route("/all_course", methods=['GET'])
def getAllCourse():
    courses = Course.query.all()
    return jsonify(
        {
            "code": 200,
            "data": [course.json() for course in courses]
        }
    ), 200

# Get one course
@app.route("/course/<int:id>", methods=['GET'])
def getoneCourse(id):
    course = Course.query.filter_by(id=id).first()
    if course:
        return jsonify(
            {
                "code": 200,
                "data": course.json()
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
        )

# Add one course
'''
sample request
{
    "name": "Engineering",
    "description": "asdfasdsahdoashdioasdhoiashdoisahdoiashdosahdioh"
}
'''
@app.route("/course", methods=['POST'])
def addCourse():
    data = request.get_json()
    course = Course(**data)
    try:
        db.session.add(course)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while creating course: {e}"
            }
        )
    
    return jsonify(
        {
            "code": 200,
            "data": course.json()
        }
    ), 200

#  Update Course
'''
sample request
{
    "id": 1,
    "name": "Engineering",
    "description": "asdfasdsahdoashdioasdhoiashdoisahdoiashdosahdioh"
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

# Delete course
@app.route("/course/<int:id>", methods=['DELETE'])
def deleteCourse(id):
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