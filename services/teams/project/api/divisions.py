from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import Division
from project import db

division_blueprint = Blueprint('divisions', __name__, template_folder='./templates')


@division_blueprint.route('/divisions', methods=['POST'])
def add_division():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    if not post_data:
        return jsonify(response_object), 400
    id = post_data.get('id')
    name = post_data.get('name')
    try:
        division = Division.query.filter_by(id_division=id, name=name).first()
        if not division:
            db.session.add(Division(id=id, name=name))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Division was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry, that Division already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@division_blueprint.route('/divisions/<division_id>', methods=['GET'])
def get_division(division_id):
    """Get single division details"""
    response_object = {
        'status': 'fail',
        'message': 'division doesnt exist'
    }
    try:
        division = Division.query.filter_by(id_division=int(division_id)).first()
        if not division:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': division.id_division,
                    'name': division.name
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@division_blueprint.route('/divisions', methods=['GET'])
def get_all_divisions():
    """Get all divisions"""
    response_object = {
        'status': 'succes',
        'data': {
            'divisions': [division.to_json() for division in Division.query.all()]
        }
    }
    return jsonify(response_object), 200