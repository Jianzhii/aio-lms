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


#  Get all quiz questions under section 
@app.route('/quiz/<int:section_id>', methods=["GET"])
def getQuiz(section_id):
    try:
        quiz_question = Quiz.query.filter_by(section_id = section_id).all()
        data = []
        return jsonify(
            {
                "code": 200,
                "message": "Quiz successfully retrieved!",
                "data": data
            }
        ), 200
    except Exception as e: 
        return jsonify(
            {
                "code":406,
                "message": f"An error occurred while retrieving Quiz: {e}"
            }
        ), 406

# Update quiz (delete from section and readd again)


# validate quiz answer