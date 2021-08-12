from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, FieldList, FormField, HiddenField
from wtforms.validators import InputRequired, optional


class filterFixtureByDivision(FlaskForm):
    divisionID = IntegerField('ID', validators=[InputRequired()])
    teamID = IntegerField('TeamID', validators=[optional()])
    submit = SubmitField('Search')

class editHomeScores(FlaskForm):
    homeScore = IntegerField('homeScore', validators=[InputRequired()])
    awayScore = IntegerField('awayScore', validators=[InputRequired()])
    matchID = HiddenField()
    opposingTeamName = HiddenField()
    submit = SubmitField('Submit')