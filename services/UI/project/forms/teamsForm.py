from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, HiddenField
from wtforms.validators import InputRequired, optional


class teamsSearchForm(FlaskForm):
    teamID = IntegerField('ID', validators=[InputRequired()])
    submit = SubmitField('Submit')

class editTeamInfo(FlaskForm):
    suffix = StringField('suffix', validators=[])
    colors = StringField('Colors', validators=[InputRequired()])
    address = StringField('address', validators=[InputRequired()])
    zipcode = IntegerField('zipcode', validators=[InputRequired()])
    city = StringField('city', validators=[InputRequired()])
    website = StringField('website', validators=[])
    name = StringField('name', validators=[InputRequired()])
    id = HiddenField('id')
    stam_nummer = HiddenField('stam_nummer')
    submit = SubmitField('Submit')