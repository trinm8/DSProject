from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, optional

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = StringField('password', validators=[InputRequired()])
    submit = SubmitField('submit')