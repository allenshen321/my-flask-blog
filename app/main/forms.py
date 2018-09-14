from flask.ext.wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('what is your username', validators=[DataRequired()])
    submit = SubmitField('Submit')
