from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import Team, Club
from project import db

teams_blueprint = Blueprint('teams', __name__, template_folder='./templates')


@teams_blueprint.route('/teams', methods=['POST'])
def add_team():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    if not post_data:
        return jsonify(response_object), 400
    id = post_data.get('id')
    stam_nummer = post_data.get('stam_nummer')
    suffix = post_data.get('suffix')
    colors = post_data.get('colors')
    try:
        team = Team.query.filter_by(id=id, stam_nummer=stam_nummer).first()
        if not team:
            db.session.add(Team(id=id, stam_nummer=stam_nummer, suffix= suffix, colors=colors))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Team was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry, that team already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@teams_blueprint.route('/teams/<team_id>', methods=['GET'])
def get_single_team(team_id):
    """Get single team details"""
    response_object = {
        'status': 'fail',
        'message': 'Team doesn\'t exist'
    }
    try:
        team = Team.query.filter_by(id=int(team_id)).first()
        if not team:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': team.id,
                    'stam_nummer': team.stam_nummer,
                    'suffix': team.suffix,
                    'colors': team.colors
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@teams_blueprint.route('/teamInfo/<team_id>', methods=['GET'])
def get_team_Info(team_id):
    """Get the info of a single team"""
    response_object = {
        'status': 'fail',
        'message': 'team doesn\'t exist'
    }
    try:
        team = Team.query.filter_by(id=int(team_id)).first()
        if not team:
            return jsonify(response_object), 404
        else:
            club = Club.query.filter_by(stam_nummer=team.stam_nummer).first()
            if not club:
                return jsonify(response_object), 404
            response_object = {
                'status': 'success',
                'data': {
                    'id': team.id,
                    'stam_nummer': team.stam_nummer,
                    'suffix': team.suffix,
                    'colors': team.colors,
                    'name': club.name,
                    'address': club.address,
                    'zipcode': club.zipcode,
                    'city': club.city,
                    'website': club.website
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@teams_blueprint.route('/teams', methods=['GET'])
def get_all_teams():
    """Get all teams"""
    response_object = {
        'status': 'success',
        'data': {
            'teams': [team.to_json() for team in Team.query.all()]
        }
    }
    return jsonify(response_object), 200

@teams_blueprint.route('/teams', methods=["PUT"])
def edit_team():
    """update team Info"""
    response_object = {
        'status': "failed",
        'message': "Something went wrong"
    }
    put_data = request.get_json()
    id = put_data.get('id')
    try:
        team = Team.query.get_or_404(id)
        team.colors = put_data.get("colors")
        team.suffix = put_data.get("suffix")
        db.session.commit()
        response_object = {
            'status': "success",
            'message': "Team Successfully updated"
        }
        return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400