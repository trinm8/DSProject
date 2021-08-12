from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import Referee
from project import db

referees_blueprint = Blueprint('referees', __name__, template_folder='./template')


@referees_blueprint.route('/referees', methods=['POST'])
def add_referee():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    if not post_data:
        return jsonify(response_object), 400
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    address = post_data.get('address')
    zipcode = post_data.get('zipcode')
    city = post_data.get('city')
    phoneNr = post_data.get('phoneNr')
    email = post_data.get('email')
    dateOfBirth = post_data.get('dateOfBirth')
    try:
        referee = Referee.query.filter_by(first_name=first_name, last_name=last_name, address=address, zipcode=zipcode,
                                          city=city, phoneNr=phoneNr, email=email, dateOfBirth=dateOfBirth).first()
        if not referee:
            db.session.add(Referee(first_name,last_name,address,zipcode,city,phoneNr,email,dateOfBirth))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Referee was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry, that referee already exists'
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@referees_blueprint.route('/referee/<referee_id>', methods=['GET'])
def get_single_referee(referee_id):
    """Get single referee details"""
    response_object = {
        'status': 'fail',
        'message': 'Referee doesnt exist'
    }
    try:
        referee = Referee.query.filter_by(id=int(referee_id)).first()
        if not referee:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': referee.to_json()
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@referees_blueprint.route('/referees', methods=['GET'])
def get_all_referees():
    """Get all referees"""
    response_object = {
        'status': 'success',
        'data': {
            'referees': [referee.to_json() for referee in Referee.query.all()]
        }
    }
    return jsonify(response_object), 200