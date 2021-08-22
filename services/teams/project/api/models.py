from project import db

#source: https://stackoverflow.com/questions/21389806/how-to-specify-the-primary-id-when-inserting-rows-with-sqlalchemy-when-id-dos-no
def new_id_factory():
    if not('_MYTABLE_ID_' in globals()):
        q = db.execute("select max(mytable.id) as max_id from mytable").fetchone()
        _MYTABLE_ID_ = (q and q.max_id) or 0
    _MYTABLE_ID_ += 1
    return _MYTABLE_ID_

class Team(db.Model):

    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stam_nummer = db.Column(db.Integer)
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


class Division(db.Model):

    __tablename__ = 'divisions'

    id_division = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)

    def __init__(self, id, name):
        self.id_division = id
        self.name = name

    def to_json(self):
        return {
            'id': self.id_division,
            'name': self.name
        }