from app import app, db
from flask import jsonify, request
from section_progress import SectionProgress, checkCompletionOfSection
from enrol import checkCompletionOfCourse


class GroupQuiz(db.Model):

    __tablename__ = 'group_quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, primary_key=True, nullable=False)
    question_no = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    choice = db.Column(db.JSON, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'question_no': self.question_no,
            'question': self.question,
            'choice': self.choice,
            'answer': self.answer,
            'duration': self.duration
        }


# Add one Quiz for section
@app.route('/group_quiz', methods=["POST"])
def addGroupQuiz():
    data = request.get_json()
    try:
        result = []
        for quiz in data:
            question = GroupQuiz(**quiz)
            db.session.add(question)
            result.append(question.json())

        db.session.commit()
        print(result)
        return jsonify(
            {
                "code": 200,
                "message": "Quiz successfully created!",
                "data": result
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 406,
                "message": f"An error occurred while creating Quiz: {e}"
            }
        ), 406


#  Get all quiz questions under section
@app.route('/group_quiz/<int:group_id>', methods=["GET"])
def getGroupQuiz(group_id):
    try:
        quiz_question = GroupQuiz.query.filter_by(group_id = group_id).order_by(GroupQuiz.question_no.asc()).all()
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
                "code": 406,
                "message": f"An error occurred while retrieving Quiz: {e}"
            }
        ), 406


# Update quiz for section
# (delete all questions from section and re-add again)
@app.route('/group_quiz/<int:group_id>', methods=["GET"])
def delGroupQuiz(group_id):
    quiz_del = GroupQuiz.query.filter_by(group_id)
    data = [question.json() for question in quiz_del]
    try:
        db.session.delete(quiz_del)
        db.session.commit
        return jsonify(
            {
                "code": 200,
                "message": "Quiz successfully deleted!",
                "data": data
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 406,
                "message": f"An error occurred while deleting Quiz: {e}"
            }
        ), 406


# Validate quiz answer
"""
sample request
{
    "section_id": 3,
    "enrolment_id": 3,
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
def validateGroupQuiz():
    data = request.get_json()
    try:
        section_id = data['section_id']
        total_correct = 0
        total_questions = len(data['answer'])
        for answer in data['answer']:
            quiz_answer = GroupQuiz.query.filter_by(section_id = section_id, question_no = answer['question_no']).first()
            if not quiz_answer:
                raise Exception('Unable to find question in database')

            answer['is_correct'] = False
            if ('selected' in answer) and (str(answer['selected']) == quiz_answer.answer.replace('"', '')):
                answer['is_correct'] = True
                total_correct += 1
            answer['answer'] = quiz_answer.answer
        data['result'] = f"{total_correct}/{total_questions}"

        section_progress = SectionProgress.query.filter_by(section_id = section_id, course_enrolment_id = data['enrolment_id']).first()
        section_progress.quiz_attempt = 1
        if not section_progress.is_quiz_pass and (total_correct / total_questions) >= 0.8:
            section_progress.is_quiz_pass = 1

        checkCompletionOfSection(section_progress)
        db.session.commit()

        checkCompletionOfCourse(data['enrolment_id'])

        return jsonify(
            {
                "code": 200,
                "message": "Quiz successfully validated!",
                "data": data
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 406,
                "message": f"An error occurred while validating Quiz: {e}"
            }
        ), 406
