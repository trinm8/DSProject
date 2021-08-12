import unittest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import User

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
    with open("data/users.csv") as file:
        reader = csv.reader(file, delimiter=',')
        next(reader)
        for row in reader:
            db.session.add(User(username=row[0], email=row[1], password=row[2], team=row[3], admin=bool(int(row[4])), superAdmin=bool(int(row[5]))))
    db.session.commit()


if __name__ == '__main__':
    cli()
