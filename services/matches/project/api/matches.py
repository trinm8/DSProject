from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import Match
from project import db

matches_blueprint = Blueprint('matches', __name__, template_folder='./templates')


@matches_blueprint.route('/matches', methods=['POST'])
def add_match():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    if not post_data:
        return jsonify(response_object), 400
    date = post_data.get('date')
    time = post_data.get('time')
    awayTeamID = post_data.get('awayTeamID')
    homeTeamID = post_data.get('homeTeamID')
    goalsHome = post_data.get('goalsHome')
    goalsAway = post_data.get('goalsAway')
    status = post_data.get('status')
    try:
        match = Match.query.filter_by(date=date, time=time, homeTeamID=homeTeamID, awayTeamID=awayTeamID).first()
        if not match:
            db.session.add(Match(date=date, time=time, awayTeamID=awayTeamID, homeTeamID=homeTeamID, goalsHome=goalsHome,
                                 goalsAway=goalsAway, status=status))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'match was added'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'There is already a match between these teams at that exact moment'
            return jsonify(response_object), 400
    except TypeError as e:
        db.session.rollback()
        return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@matches_blueprint.route('/matches/<match_id>', methods=['GET'])
def get_single_match_with_ID(match_id):
    """Get single match"""
    response_object = {
        'status': 'fail',
        'message': 'match does not exist'
    }
    try:
        match = Match.query.filter_by(id=int(match_id)).first()
        if not match:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': match.id,
                    'date': match.date,
                    'time': match.time,
                    'awayTeamID': match.awayTeamID,
                    'homeTeamID': match.homeTeamID,
                    'awayGoals': match.goalsAway,
                    'homeGoals': match.goalsHome,
                    'status': match.status
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@matches_blueprint.route('/matches', methods=['GET'])
def get_all_matches():
    """Get all matches"""
    response_object = {
        'status': 'success',
        'data': {
            'users': [match.to_json() for match in Match.query.all()]
        }
    }
    return jsonify(response_object), 200


@matches_blueprint.route('/', methods=['GET', 'POST'])
def index():
    pass


@matches_blueprint.route('/matches/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })