from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,RadioField

from wtforms.validators import Length, Email, ValidationError, EqualTo, DataRequired

class Quiz_form(FlaskForm):
    title = StringField('title',validators=[DataRequired(),Length(4,76)])
    submit = SubmitField('create_quiz')

class Question_form(FlaskForm):
    text = TextAreaField('question_text',validators=[DataRequired(),Length(3,100)])
    answer1_text = StringField('answer_text',validators=[DataRequired(),Length(1,100)])
    answer2_text = StringField('answer_text',validators=[DataRequired(),Length(1,100)])
    answer3_text = StringField('answer_text',validators=[DataRequired(),Length(1,100)])
    answer4_text = StringField('answer_text',validators=[DataRequired(),Length(1,100)])

    Correct_answer = RadioField('correct_answer',choices=[('1','answer1'),('2','answer2'),('3','answer3'),('4','answer4')])
    submit = SubmitField('Add_question')
    add_more = SubmitField('Add_more_questions')

class Join_game_form(FlaskForm):
    code = StringField('Game Code', validators=[DataRequired(),Length(6, 7)])
    username = StringField('Your Name', validators=[DataRequired(), Length(3, 45)])
    submit = SubmitField('Join game')
