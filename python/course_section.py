from flask import Flask, redirect, url_for, render_template, request 
from app import app, db
from flask import jsonify, request
from user import User

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True) 

class CourseSection(db.Model):

    __tablename__ = 'course_section'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    video_url = db.Column(db.String(100), nullable=False)
    material_url = db.Column(db.String(100), nullable=False)

    def json(self): 
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'video_url': self.video_url,
            'material_url': self.material_url
        }

#Get all Sections
@app.route("/all_section", methods=['GET'])
def getAllSection(): 
    course_sections = CourseSection.query.all()
    return jsonify(
        {
            "code": 200,
            "data": [course_section.json() for course_section in course_sections]            
        }
    ), 200

# Get one section
@app.route("/course_section/<int:id>", methods=['GET'])
def getoneSection(id):
    course_section = CourseSection.query.filter_by(id=id).first()
    if course_section:
        return jsonify(
            {
                "code": 200,
                "data": course_section.json()
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
@app.route("/course_section", methods=['POST'])
def addSection():
    data = request.get_json()
    course_section = CourseSection(**data)
    try:
        db.session.add(course_section)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while creating section: {e}"
            }
        )
    
    return jsonify(
        {
            "code": 200,
            "data": course_section.json()
        }
    ), 200


#  Update Section
@app.route("/course_section", methods=['PUT'])
def updateSection():
    try:
        data = request.get_json()
        id = data['id']
        course_section = CourseSection.query.filter_by(id=id).first()
        if not course_section:
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Section not found."
                }
            )
        course_section.name = data['name']
        course_section.description = data['description']
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

# Delete section
@app.route("/course_section/<int:id>", methods=['DELETE'])
def deleteSection(id):
    course_section = CourseSection.query.filter_by(id=id).first()
    if not course_section:
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
        db.session.delete(course_section)
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
