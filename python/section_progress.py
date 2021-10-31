from app import app, db
from course_section import CourseSection, Materials
from flask.json import jsonify
from sqlalchemy.ext.mutable import MutableDict

class ChapterProgress(db.Model):
    __tablename__ = 'section_progress'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, nullable=False)
    course_enrolment_id = db.Column(db.Integer, nullable=False)
    material = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)
    quiz_attempt = db.Column(db.Boolean, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'course_enrolment_id': self.course_enrolment_id,
            'material' : self.material,
            'quiz_attempt': self.quiz_attempt,
        }


# Create records in chapter progress table
def createProgressRecord(data):
    try:
        sections = CourseSection.query.filter_by(group_id = data['group_id']).all()
        for section in sections:
            section_material = {}
            materials = Materials.query.filter_by(section_id = section.id).all()
            for material in materials:
                section_material[material.id] = False
            progress = ChapterProgress(
                section_id = section.id,
                course_enrolment_id = data['id'],
                material = section_material,
                quiz_attempt = False
            )
            db.session.add(progress)
        db.session.commit()
    except Exception as e:
        raise e


# Get section progress
@app.route("/section_progress/<int:enrolment_id>/<int:section_id>", methods=['GET'])
def getProgress(enrolment_id, section_id):
    try: 
        progress = ChapterProgress.query.filter_by(course_enrolment_id = enrolment_id, section_id = section_id).first().json()
        for material_id in progress['material']:
            material = Materials.query.filter_by(id = material_id).first()
            progress['material'][material_id] = {
                "title": material.title,
                "material_type": material.material_type,
                "url": material.url,
                "completed": progress['material'][material_id]
            }

        return jsonify(
            {
                "code": 200,
                "message": "Successfully retrieved section progress.",
                "data": progress
            }
        ),200
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while retrieving progress: {e}"
            }
        ), 500


#  Mark material as completed
@app.route("/completed/<int:progress_id>/<int:material_id>", methods=['PUT'])
def markCompleted(progress_id, material_id):
    try:
        progress = db.session.query(ChapterProgress).filter(ChapterProgress.id == progress_id).first()
        progress.material[str(material_id)] = True
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Successfully marked material as completed.",
                "data": progress.json()
            }
        ),200
    except Exception as e: 
        return jsonify( 
            {
                "code":500,
                "message": f"An error occurred while marking material as complete: {e}"
            }
        ), 500