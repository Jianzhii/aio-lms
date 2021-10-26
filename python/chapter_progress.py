from app import app, db
from sqlalchemy import and_,or_
from user import User
from course import Course
from group import Group
from sqlalchemy import or_
from datetime import datetime
from course_section import CourseSection
from enrolment_request import EnrolmentRequest



class ChapterProgress(db.Model):
    __tablename__ = 'chapter_progress'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, primary_key=True)
    course_enrolment_id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.JSON, nullable=False)
    quiz_result = db.Column(db.Float, nullable=True)
    is_pass = db.Column(db.Integer, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'course_enrolment_id': self.course_enrolment_id,
            'material' : self.material,
            'quiz_result': self.quiz_result,
            'is_pass': self.is_pass
        }