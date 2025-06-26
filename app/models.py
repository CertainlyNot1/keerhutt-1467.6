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

class GameSesh(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)
    code = db.Column(db.String(7), unique = True, nullable = False)
    is_active = db.Column(db.Boolean, default = True)
    curr_question = db.Column(db.Integer, default = 0)
    quiz = db.relationship('Quiz', backref = 'game_sesh')
    players = db.relationship('Player', backref = 'game_seshes', lazy = True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50)) #Jenna Talia, Phil MCcrackin
    score = db.Column(db.Integer, default = 0)
    game_sesh_id = db.Column(db.Integer, db.ForeignKey('game_sesh.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    sid = db.Column(db.String)