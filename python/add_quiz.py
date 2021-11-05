from app import app, db
from flask import jsonify, request



class Quiz(db.Model):

    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id = db.Column(db.Integer, primary_key=True, nullable=False)
    question_no = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    choice = db.Column(db.JSON, nullable=False)
    answer = db.Column(db.Text, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'question_no': self.question_no,
            'question': self.question,
            'choice': self.choice,
            'answer': self.answer
        }


#Add one Quiz for section
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
        quiz_question = Quiz.query.filter_by(section_id = section_id).order_by(Quiz.question_no.asc()).all()
        data = [question.json() for question in quiz_question]
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


# Update quiz for section 
# (delete all questions from section and re-add again)



# Validate quiz answer
"""
sample request
{   
    "section_id": 3,
    answers: [
       {
           "question_no": 1,
            "selected": "True"
        },
        {
            "question_no": 2,
            "selected": "asd"
        }
    ]
}
"""
@app.route('/validate_quiz', methods=["POST"])
def validateQuiz():
    data = request.get_json()
    try:
        print(data)
        section_id = data['section_id']
        total_correct = 0
        total_questions = len(data['answers'])
        for answer in data['answer']:
            quiz_answer = Quiz.query.filter_by(section_id = section_id, question_no = answer['question_no']).first()
            if not quiz_answer:
                raise Exception('Unable to find question in database')
                
            answer['is_correct'] = False
            if answer['selected'] and (answer['selected'] == quiz_answer.answer):
                answer['is_correct'] = True
                total_correct += 1
            answer['answer'] = quiz_answer.answer
        data['result'] = f"{total_correct}/{total_questions}"
        
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
                "message": f"An error occurred while validating Quiz: {e}"
            }
        ), 406