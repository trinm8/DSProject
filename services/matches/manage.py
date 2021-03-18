import unittest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import Match

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
    for name in ["data/matches_2020_2021.csv", "data/matches_2019_2020.csv", "data/matches_2018_2019.csv"]:
        with open(name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                arguments = [row[2], row[3], row[5], row[4], row[6], row[7], row[8], row[0]]
                if len(row) == 10:
                    arguments.append(row[9])
                db.session.add(Match(*arguments))
    #db.session.add(Match(username='michael', email="hermanmu@gmail.com"))
    #db.session.add(Match(username='michaelherman', email="michael@mherman.org"))
    db.session.commit()


if __name__ == '__main__':
    cli()