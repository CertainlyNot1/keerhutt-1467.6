from .extensions import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(411),unique=True, nullable= False)
    password = db.Column(db.String(25), nullable = False)
    quizzes = db.relationship('Quiz', backref='creator', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(75), nullable=False)
    username = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    questions = db.relationship('Question', backref='question',lazy = True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(150), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)
    answers = db.relationship('Answer', backref='question',lazy = True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(50), nullable=False)
    is_right = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
