from project import db


class Team(db.Model):

    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stam_nummer = db.Column(db.Integer, primary_key=True)
    suffix = db.Column(db.String(128), nullable=True)
    colors = db.Column(db.String(128), nullable=False)

    def __init__(self, id, stam_nummer, suffix, colors):
        self.id = id
        self.stam_nummer = stam_nummer
        self.suffix = suffix
        self.colors = colors

    def to_json(self):
        return {
            'id': self.id,
            'stam_nummer': self.stam_nummer,
            'suffix': self.suffix,
            'colors': self.colors
        }


class Club(db.Model):

    __tablename__ = 'clubs'

    stam_nummer = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    address = db.Column(db.String)
    zipcode = db.Column(db.Integer)
    city = db.Column(db.String)
    website = db.Column(db.String)

    def __init__(self, stam_nummer, name, address, zipcode, city, website):
        self.stam_nummer = stam_nummer
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.city = city
        self.website = website

    def to_json(self):
        return {
            'stam_nummer': self.stam_nummer,
            'name': self.name,
            'address': self.address,
            'zipcode': self.zipcode,
            'city': self.city,
            'website': self.website
        }
