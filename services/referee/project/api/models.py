from project import db
import datetime


class Referee(db.Model):

    __tablename__ = 'referees'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    address = db.Column(db.String)
    zipcode = db.Column(db.Integer)
    city = db.Column(db.String)
    phoneNr = db.Column(db.String)
    email = db.Column(db.String)
    dateOfBirth = db.Column(db.DateTime)

    def __init__(self, first_name, last_name, address, zipcode, city, phoneNr, email, dateOfBirth):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.zipcode = zipcode
        self.city = city
        self.phoneNr = phoneNr
        self.email = email
        self.dateOfBirth = datetime.datetime.strptime(dateOfBirth, "%Y-%m-%d")
        
    def to_json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'zipcode': self.zipcode,
            'city': self.city,
            'phoneNr': self.phoneNr,
            'email': self.email,
            'dateOfBirth': self.dateOfBirth
        }