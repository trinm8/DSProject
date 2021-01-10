from flask import Blueprint, jsonify, request, render_template

import requests

ui_blueprint = Blueprint('UI', __name__, template_folder='./templates')


@ui_blueprint.route('/', methods=['GET'])
def index():
    return render_template('home.html')


@ui_blueprint.route('/LeagueTables', methods=['GET'])
def leagueTables():
    divisions = requests.get("http://192.168.0.1:5000/users")
    print(divisions.text)
    if divisions.status_code == 200:
        print("succes")
        return render_template('leagueTables.html', divisions=divisions.json()["data"]["divisions"])
    else:
        print("failed")
        return render_template('leagueTables.html', divisions=None)

