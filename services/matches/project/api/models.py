import datetime
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

    def __init__(self, date, time, awayTeamID, homeTeamID, goalsHome, goalsAway, status):
        self.date = datetime.datetime.strptime(date, "%d-%m-%Y")
        self.time = datetime.datetime.strptime(time, "%H:%M:%S")
        self.awayTeamID = awayTeamID
        self.homeTeamID = homeTeamID
        self.goalsHome = goalsHome
        self.goalsAway = goalsAway
        self.status = status

    def to_json(self):
        return {
            'id': self.id,
            'date': self.date,
            'time': self.time,
            'awayTeamID': self.awayTeamID,
            'homeTeamID': self.homeTeamID,
            'goalsHome': self.goalsHome,
            'goalsAway': self.goalsAway,
            'status': self.status
        }
