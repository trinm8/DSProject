import unittest
import os
import csv

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import Referee

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """Runs the test without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def seed_db():
    """Seeds the database."""
    for filename in os.listdir('project/data'):
        try:
            if filename.endswith(".csv"):
                file = open('project/data/' + filename)
                data = csv.reader(file, delimiter=',')
                data = list(data)
                dataiter = iter(data)
                next(dataiter)
                for i in dataiter:
                    record = Referee(first_name=i[0], last_name=i[1], address=i[2], zipcode=i[3], city=i[4],
                                     phoneNr=i[5], email=i[6], dateOfBirth=i[7])
                    db.session.add(record)
        except:
            print("failed")
            db.session.rollback()
    db.session.commit()

if __name__ == '__main__':
    cli()