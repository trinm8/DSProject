from sqlalchemy.sql import func


from project import db
import datetime

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    team = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password, team, admin):
        self.username = username
        self.email = email
        self.active = False
        self.created_date = datetime.datetime.now()
        self.password = password
        self.team = team
        self.admin = admin

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'active': self.active,
            'created date': self.created_date,
            'password': self.password,
            'team': self.team,
            'admin': self.admin
        }