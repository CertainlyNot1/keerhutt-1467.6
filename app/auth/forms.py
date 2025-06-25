from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, Email, ValidationError, EqualTo, DataRequired
from ..models import User
class Register_Form(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(3,25)])
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired(),Length(8,75)])
    confirm_password = PasswordField('confirm_password',validators=[DataRequired(),Length(8,75),EqualTo('password')])
    submit = SubmitField('Sign up!')
    def Validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("hey there, sadly i know what you did on september 3rd 2019, so we cannot let you use someone else's username, use a different one, identity thief.")
        
class Login_Form(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(3,25)])
    password = PasswordField('password',validators=[DataRequired(),Length(8,75)])
    remember_me = BooleanField('remember me')
    submit = SubmitField('')