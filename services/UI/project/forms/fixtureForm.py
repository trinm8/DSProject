from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, optional


class filterFixtureByDivision(FlaskForm):
    divisionID = IntegerField('ID', validators=[InputRequired()])
    teamID = IntegerField('TeamID', validators=[optional()])
    submit = SubmitField('Search')