from types import prepare_class
from app import app, db
from flask import jsonify, request
from user import User

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
        )

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
        )

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
                "data": course.json()
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while creating course: {e}"
            }
        )

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
            )
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
    try:
        course = Course.query.filter_by(id=id).first()
        badge = Badge.query.filter_by(course_id=id).first()
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