from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from wtforms import validators

import requests


class ModelViewAuthorized(ModelView):
    column_display_pk = True

    def is_accessible(self):
        userdata = request.cookies.get('username')
        if userdata:
            loginData = {
                'username': userdata,
                'password': request.cookies.get('password')
            }
            loginAttempt = requests.post('http://users:5000/users/authenticate', json=loginData)
            if loginAttempt.status_code == 200:
                return True
            else:
                return False
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('UI.login'))


class ModelViewAuthorizedSuperAdmin(ModelView):

    def is_accessible(self):
        userdata = request.cookies.get('username')
        if userdata:
            loginData = {
                'username': userdata,
                'password': request.cookies.get('password')
            }
            loginAttempt = requests.post('http://users:5000/users/authenticate', json=loginData)
            if loginAttempt.status_code == 200 and loginAttempt.json()["data"]["superAdmin"]:
                return True
            else:
                return False
        else:
            return False


class ModelViewAuthorizedMatches(ModelViewAuthorized):

    def on_model_change(self, form, model, is_created):
        response = requests.get("http://matches:5000/matches/assignedReferees" + "?date=" + str(form.date.data))
        if response.status_code == 200 and form.assignedRefereeID.data in list(response.json()["data"]):
            raise validators.ValidationError('Referee is already assigned for that date')