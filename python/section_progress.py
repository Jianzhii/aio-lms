from flask import jsonify, request
from sqlalchemy.ext.mutable import MutableDict

from app import app, db
from course_section import CourseSection, Materials


class SectionProgress(db.Model):
    __tablename__ = "section_progress"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, primary_key=True)
    course_enrolment_id = db.Column(db.Integer, primary_key=True)
    material = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)
    quiz_attempt = db.Column(db.Boolean, nullable=False)
    is_quiz_pass = db.Column(db.Boolean, nullable=False)
    is_access = db.Column(db.Boolean, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "section_id": self.section_id,
            "course_enrolment_id": self.course_enrolment_id,
            "material": self.material,
            "quiz_attempt": self.quiz_attempt,
            "is_quiz_pass": self.is_quiz_pass,
            "is_access": self.is_access,
        }


# Create records in section progress tables
def createProgressRecord(data):
    try:
        sections = CourseSection.query.filter_by(group_id=data["group_id"]).all()
        if sections:
            first_section = min([section.id for section in sections])
            for section in sections:
                progress_check = SectionProgress.query.filter_by(course_enrolment_id=data['id'], section_id=section.id).first()
                if not progress_check:
                    section_material = {}
                    materials = Materials.query.filter_by(section_id=section.id).all()
                    for material in materials:
                        section_material[material.id] = False
                    progress = SectionProgress(
                        section_id = section.id,
                        course_enrolment_id = data["id"],
                        material = section_material,
                        quiz_attempt = False,
                        is_quiz_pass = False,
                        is_access = True if section.id == first_section else False
                    )
                    db.session.add(progress)
            db.session.commit()
    except Exception as e:
        raise e


# Get section progress
@app.route("/section_progress/<int:enrolment_id>/<int:section_id>", methods=["GET"])
def getProgress(enrolment_id, section_id):
    try:
        progress = (
            SectionProgress.query.filter_by(
                course_enrolment_id=enrolment_id, section_id=section_id
            )
            .first()
            .json()
        )
        section = CourseSection.query.filter_by(id=progress['section_id']).first()
        progress['section_name'] = section.name
        progress['description'] = section.description
        if not progress:
            raise Exception('Cannot find section progress.')
        total_material = 0
        total_completed = 0
        material_url = []
        video_url = []
        for material_id in progress["material"]:
            total_material += 1
            if progress['material'][material_id]:
                total_completed += 1

            material = Materials.query.filter_by(id=material_id).first()
            if material.material_type == "Video":
                video = material.json()
                video['completed'] = progress["material"][material_id]
                video_url.append(video)
            else:
                material = material.json()
                material['completed'] = progress["material"][material_id]
                material_url.append(material)

        del progress['material']
        progress["material_url"] = material_url
        progress['video_url'] = video_url
        if not total_material or not total_completed:
            progress['completion_status'] = 0
        else:
            progress['completion_status'] = round(total_completed / total_material, 2)
        progress['is_completed'] = (total_completed == total_material)

        return jsonify(
                {
                    "code": 200,
                    "message": "Successfully retrieved section progress.",
                    "data": progress,
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while retrieving progress: {e}",
                }
            ), 406


#  Mark material as completed
@app.route("/completed/<int:progress_id>/<int:material_id>", methods=["PUT"])
def markCompleted(progress_id, material_id):
    try:
        progress = (
            db.session.query(SectionProgress)
            .filter(SectionProgress.id == progress_id)
            .first()
        )
        progress.material[str(material_id)] = True
        checkCompletionOfSection(progress)
        db.session.commit()

        from enrol import checkCompletionOfCourse
        checkCompletionOfCourse(progress.course_enrolment_id)

        return jsonify(
                {
                    "code": 200,
                    "message": "Successfully marked material as completed.",
                    "data": progress.json(),
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while marking material as complete: {e}",
                }
            ), 406

def checkCompletionOfSection(section_progress):
    try:
        # check all complete, dhen mark second true
        check_all_complete = True
        for material_id in section_progress.material:
            if not section_progress.material[material_id]:
                check_all_complete = False
                break
        if not section_progress.quiz_attempt:
            check_all_complete = False

        if check_all_complete:
            next = db.session.query(SectionProgress).filter(SectionProgress.id > section_progress.id, SectionProgress.course_enrolment_id == section_progress.course_enrolment_id).first()
            if next:
                next.is_access = True
    except Exception as e:
        raise e

#  Get all section under learner
@app.route("/section_progress/all_section/<int:enrolment_id>", methods=["GET"])
def getAllSectionUnderEnrolment(enrolment_id):
    try:
        all_section = (db.session.query(SectionProgress, CourseSection)
            .filter(SectionProgress.course_enrolment_id == enrolment_id)
            .outerjoin(CourseSection, CourseSection.id == SectionProgress.section_id)
            .all()
        )
        data = []
        for section_progress, section in all_section:
            section_progress = section_progress.json()
            section_progress["section_name"] = section.name
            section_progress["section_description"] = section.description
            del section_progress['material']
            del section_progress['quiz_attempt']
            del section_progress['is_quiz_pass']
            data.append(section_progress)
        return jsonify(
            {
                "code": 200,
                "message": "Successfully retrieved all sections.",
                "data": data,
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 406,
                "message": f"An error occurred while retrieving sections: {e}",
            }
        ), 406
