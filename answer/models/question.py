import random

from answer.extensions import db


class QuickQuestion(db.Model):
    __tablename__ = "quick_questions"
    question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    asked = db.Column(db.Boolean, default=False)

    def __init__(self, question):
        self.question = question
        self.asked = False


class Question(db.Model):

    __tablename__ = "questions"

    question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    question = db.Column(db.Text, nullable=False)

    correct_answer = db.Column(db.Text, nullable=False)
    wrong_answer1 = db.Column(db.Text, nullable=False)
    wrong_answer2 = db.Column(db.Text, nullable=False)
    wrong_answer3 = db.Column(db.Text, nullable=False)
    wrong_answer4 = db.Column(db.Text, nullable=False)

    asked = db.Column(db.Boolean, default=False)

    def __init__(self, question, correct, wrong1, wrong2, wrong3, wrong4):
        self.question = question
        self.correct_answer = correct
        self.wrong_answer1 = wrong1
        self.wrong_answer2 = wrong2
        self.wrong_answer3 = wrong3
        self.wrong_answer4 = wrong4
        self.asked = False

    def __repr__(self):
        return f"<Question {self.question_id}>"

    def get_dict(self):
        possible_answers = [self.correct_answer, self.wrong_answer1, self.wrong_answer2,
                            self.wrong_answer3, self.wrong_answer4]
        random.shuffle(possible_answers)
        return {
            'question': self.question,
            'answers': possible_answers
        }
