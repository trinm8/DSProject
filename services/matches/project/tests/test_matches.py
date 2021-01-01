import json
import unittest

from project import db
from project.tests.base import BaseTestCase
from project.api.models import Match


def add_user(date, time, awayTeamID, homeTeamID, awayGoal, homeGoal, status):
    match = Match(date=date, time=time, awayTeamID=awayTeamID, homeTeamID=homeTeamID, goalsAway=awayGoal,
                  goalsHome=homeGoal, status=status)
    db.session.add(match)
    db.session.commit()
    return match


class TestMatchService(BaseTestCase):
    """Tests for match service"""

    def test_matches(self):
        """Ensure a new match can be added"""
        response = self.client.get('/matches/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_match(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'date': '01-01-2020',
                    'time': '00:00:00',
                    'awayTeamID': 1,
                    'homeTeamID': 2,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('match was added', data['message'])
            self.assertIn('success', data['status'])

    def test_add_match_invalid_json_keys(self):
        """Ensure error is thrown when data is missing in JSON object"""
        with self.client:
            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'time': '00:00:00',
                    'awayTeamID': 1,
                    'homeTeamID': 2,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'date': '01-01-2020',
                    'awayTeamID': 1,
                    'homeTeamID': 2,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'date': '01-01-2020',
                    'time': '00:00:00',
                    'homeTeamID': 2,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'date': '01-01-2020',
                    'time': '00:00:00',
                    'awayTeamID': 1,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_match_duplicates(self):
        """Ensure there are no duplicates"""
        with self.client:
            self.client.post(
                '/matches',
                data=json.dumps({
                    'date': '01-01-2020',
                    'time': '00:00:00',
                    'awayTeamID': 0,
                    'homeTeamID': 1,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/matches',
                data=json.dumps({
                    'date': '01-01-2020',
                    'time': '00:00:00',
                    'awayTeamID': 0,
                    'homeTeamID': 1,
                    'goalsHome': 0,
                    'goalsAway': 0,
                    'status': 0
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('There is already a match between these teams at that exact moment', data['message'])
            self.assertIn('fail', data['status'])