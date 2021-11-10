from flask import jsonify, request

from app import app, db


class CourseSection(db.Model):

    __tablename__ = "section"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "name": self.name,
            "description": self.description,
        }


class Materials(db.Model):

    __tablename__ = "material"
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    material_type = db.Column(db.Enum("Video", "Document"), nullable=False)
    url = db.Column(db.String(100), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "section_id": self.section_id,
            "title": self.title,
            "material_type": self.material_type,
            "url": self.url,
        }


# Get all Sections
@app.route("/all_section/<int:group_id>", methods=["GET"])
def getAllSection(group_id):
    course_sections = CourseSection.query.filter(
        CourseSection.group_id == group_id
    ).all()
    return jsonify(
            {
                "code": 200,
                "message": "Successfully retrieved sections",
                "data": [course_section.json() for course_section in course_sections],
            }
    ), 200

# Get one section
@app.route("/course_section/<int:id>", methods=["GET"])
def getOneSection(id):
    course_section = CourseSection.query.filter_by(id=id).first()
    if course_section:
        materials = Materials.query.filter_by(section_id=id).all()
        material_url = []
        video_url = []
        for material in materials:
            if material.material_type == "Video":
                video_url.append(material.json())
            else:
                material_url.append(material.json())
        course_section_json = course_section.json()
        course_section_json["material_url"] = material_url
        course_section_json["video_url"] = video_url
        return jsonify(
                {
                    "code": 200,
                    "message": "Successfully retrieved sections",
                    "data": course_section_json,
                }
        ), 200
    else:
        return jsonify(
                {
                    "code": 406,
                    "data": {"id": id}, "message": "Section not found."
                }
            ), 406


# Add one section
@app.route("/course_section", methods=["POST"])
def addSection():
    data = request.get_json()
    course_section = CourseSection(**data)
    try:
        db.session.add(course_section)
        db.session.commit()

        from enrol import Enrolment
        from section_progress import createProgressRecord

        all_current_enrolment = Enrolment.query.filter_by(
            group_id=data["group_id"]
        ).all()
        for enrolment in all_current_enrolment:
            createProgressRecord(enrolment.json())

        return jsonify(
                {
                    "code": 200,
                    "message": "Successfully added section.",
                    "data": course_section.json(),
                }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while creating section: {e}",
                }
            ), 406


#  Update Section
@app.route("/course_section", methods=["PUT"])
def updateSection():
    try:
        data = request.get_json()
        id = data["id"]
        course_section = CourseSection.query.filter_by(id=id).first()
        if not course_section:
            return jsonify(
                {
                    "code": 406,
                    "data": {"id": id}, "message": "Section not found."
                }
            ), 406
        course_section.name = data["name"]
        course_section.description = data["description"]
        db.session.commit()

        return jsonify(
                {
                    "code": 200,
                    "data": data,
                    "message": "Section successfully updated"
                }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while updating section: {e}",
                }
        ), 406


# Delete section
@app.route("/course_section/<int:id>", methods=["DELETE"])
def deleteSection(id):
    try:
        course_section = CourseSection.query.filter_by(id=id).first()
        if not course_section:
            return jsonify(
                {
                    "code": 406,
                    "data": {"id": id},
                    "message": "Section not found."
                }
            ), 406

        from enrol import Enrolment
        from section_progress import SectionProgress

        all_current_enrolment = Enrolment.query.filter_by(
            group_id=course_section.group_id
        ).all()
        for enrolment in all_current_enrolment:
            all_progress = SectionProgress.query.filter_by(
                course_enrolment_id=enrolment.id, section_id=id
            ).all()
            for progress in all_progress:
                db.session.delete(progress)
        db.session.commit()

        materials = Materials.query.filter_by(section_id=id).all()
        if materials:
            for material in materials:
                db.session.delete(material)
        db.session.commit()
        db.session.delete(course_section)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Section successfully deleted"
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting section: {e}",
                }
        ), 406
