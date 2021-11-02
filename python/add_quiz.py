from app import app, db
from flask import jsonify, request



class Quiz(db.Model):

    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, primary_key=True, nullable=False)
    question_choice = db.Column(db.JSON, nullable=False)
    answer = db.Column(db.JSON, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'question_choice': self.question_choice,
            'answer': self.answer
        }


#Add one Quiz
@app.route('/add_quiz', methods=["POST"])
def addQuiz():
    print(request.get_json())
    data = request.get_json()
    print(data)
    try:
        quiz = Quiz(**data)
        db.session.add(quiz)
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