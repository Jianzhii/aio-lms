from operator import and_
from types import prepare_class
from app import app, db
from flask import json, jsonify, request
from sqlalchemy.sql.expression import outerjoin, and_
from user import User
from datetime import datetime



class Quiz(db.Model):

    __tablename__ = 'quiz'
    id = db.Column(db.Interger, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, primary_key=True, nullable=False)
    question_choice = db.Column(db.Json, nullable=False)
    answer = db.Column(db.Json, nullable=True)
    passing_grade = db.Column(db.Float, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'question_choice': self.question_choice,
            'answer': self.answer,
            'passing_grade': self.passing_grade
        };

#Add one Quiz
@app.route('/add_quiz', methods=["POST"])
def addQuiz():
    data = request.get_json()
    try:
        quiz = Quiz(**data)
        db.session.add(quiz)
        db.session.commit()
        add_quiz = Quiz(
            CID = quiz.id,
            QC = quiz.question_choice,
            QA = quiz.answer
        )
        db.session.add(add_quiz)
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Quiz successfully created!",
                "data": quiz.json()
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "message": f"An error occurred while creating Quiz: {e}"
            }
        ), 500