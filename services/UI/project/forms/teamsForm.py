from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, optional


class teamsSearchForm(FlaskForm):
    teamID = IntegerField('ID', validators=[InputRequired()])
    submit = SubmitField('Submit')