import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from project import db


class Match(db.Model):

    __tablename__ = 'match'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    awayTeamID = db.Column(db.Integer, nullable=False)
    homeTeamID = db.Column(db.Integer, nullable=False)
    goalsHome = db.Column(db.Integer, nullable=True)
    goalsAway = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, nullable=True)
    divisionID = db.Column(db.Integer, nullable=True)
    assignedRefereeID = db.Column(db.Integer, nullable=True)

    def __init__(self, date, time, awayTeamID, homeTeamID, goalsHome, goalsAway, status, divisionID = None, assignedRefereeID = None):
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.time = datetime.datetime.strptime(time, "%H:%M:%S")
        self.awayTeamID = awayTeamID
        self.homeTeamID = homeTeamID
        if goalsHome == 'NULL':
            self.goalsHome = 0
        else:
            self.goalsHome = goalsHome
        if goalsAway == 'NULL':
            self.goalsAway = 0
        else:
            self.goalsAway = goalsAway
        if status == 'NULL':
            self.status = 0
        else:
            self.status = status
        self.divisionID = divisionID
        self.assignedRefereeID = assignedRefereeID

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date,
            'time': self.time.strftime("%H:%M:%S"),
            'awayTeamID': self.awayTeamID,
            'homeTeamID': self.homeTeamID,
            'goalsHome': self.goalsHome,
            'goalsAway': self.goalsAway,
            'status': self.status,
            'divisionID': self.divisionID,
            'refereeID': self.assignedRefereeID
        }

    @hybrid_property
    def datetime_as_timestamp(self):
        return datetime.datetime.combine(self.date, self.time)

    @datetime_as_timestamp.expression
    def datetime_as_timestamp(cls):
        return cls.date + cls.time