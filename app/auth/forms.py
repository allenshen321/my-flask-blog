from flask.ext.wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User
from wtforms import ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp(r'^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must be letter, numbers, dot or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='password must match')])
    password2 = PasswordField('Password again', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


class ChangePassword(FlaskForm):
    old_password = StringField('old password', validators=[DataRequired()])
    new_password = PasswordField('new password', validators=[DataRequired(), EqualTo('new_password2', message='password must match')])
    new_password2 = PasswordField('new password again', validators=[DataRequired()])
    submit = SubmitField('确认修改')
