from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from project.api.models import Club
from project import db

clubs_blueprint= Blueprint('clubs', __name__, template_folder='./templates')


@clubs_blueprint.route('/clubs', methods=['POST'])
def add_club():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }
    if not post_data:
        return jsonify(response_object), 400
    stam_nummer = post_data.get('stam_nummer')
    name = post_data.get('name')
    address = post_data.get('address')
    zipcode = post_data.get('zipcode')
    city = post_data.get('city')
    website = post_data.get('website')
    try:
        club = Club.query.filter_by(stam_nummer=stam_nummer).first()
        if not club:
            db.session.add(Club(stam_nummer=stam_nummer, name=name, address=address, zipcode=zipcode, city=city,
                                website=website))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Club {name} was added'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That Club already exists'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@clubs_blueprint.route('/clubs/<stam_nr>', methods=['GET'])
def get_single_club(stam_nr):
    """Get single club detail"""
    response_object = {
        'status': 'fail',
        'message': 'Club does not exist'
    }
    try:
        club = Club.query.filter_by(stam_nummer=int(stam_nr)).first()
        if not club:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'stam_nummer': club.stam_nummer,
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


@clubs_blueprint.route('/clubs', methods=['GET'])
def get_all_clubs():
    """get all clubs"""
    response_object = {
        'status': 'succes',
        'data': {
            'clubs': [club.to_json() for club in Club.query.all()]
        }
    }
    return jsonify(response_object), 200

@clubs_blueprint.route('/clubs', methods=['PUT'])
def edit_club():
    put_data = request.get_json()
    stam_nummer = put_data.get('stam_nummer')
    response_object = {
        'status': "failed",
        'message': "update failed"
    }
    try:
        club = Club.query.get_or_404(stam_nummer)
        club.name = put_data.get("name")
        club.address = put_data.get("address")
        club.zipcode = put_data.get("zipcode")
        club.website = put_data.get("website")
        club.city = put_data.get("city")
        db.session.commit()
        response_object = {
            'status': "success",
            'message': "update successful"
        }
        return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400