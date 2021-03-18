import unittest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import Team, Division, Club

import csv

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
    with open("data/divisions.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            db.session.add(Division(row[0], row[1]))
    with open("data/teams.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            db.session.add(Team(row[0], row[1], row[2], row[3]))
    with open("data/clubs.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            db.session.add(Club(row[0], row[1], row[2], row[3], row[4], row[5]))
    #db.session.add(Match(username='michael', email="hermanmu@gmail.com"))
    #db.session.add(Match(username='michaelherman', email="michael@mherman.org"))
    db.session.commit()


if __name__ == '__main__':
    cli()