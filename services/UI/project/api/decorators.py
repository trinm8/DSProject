from functools import wraps
from flask import flash, request,redirect, url_for

import requests


def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        userdata = request.cookies.get('username')
        if userdata:
            loginData = {
                'username': userdata,
                'password': request.cookies.get('password')
            }
            loginAttempt = requests.post('http://users:5000/users/authenticate', json=loginData)
            if loginAttempt.status_code == 200:
                return function_to_protect(*args, **kwargs)
            else:
                flash("Session active, but user data has since become invalid")
                return redirect(url_for('UI.login'))
        else:
            flash("Please log in")
            return redirect(url_for('UI.login'))
    return wrapper