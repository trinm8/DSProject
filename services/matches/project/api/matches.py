from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_, func, and_, desc, asc, Date, Time, cast

from project.api.models import Match
from project import db

import requests, datetime, sqlalchemy

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
            db.session.add(
                Match(date=date, time=time, awayTeamID=awayTeamID, homeTeamID=homeTeamID, goalsHome=goalsHome,
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
                'data': match.to_json()
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


@matches_blueprint.route('/matches/division/<division_id>', methods=['GET'])
def get_matches_from_division(division_id):
    """get matches with from a specific division"""
    request_object = {
        'status': 'failed'
    }
    division = requests.get("http://teamsclubs:5000/divisions/" + str(division_id))
    if not division:
        request_object["message"] = "Division doesn't exist"
        return jsonify(request_object), 404
    matches = Match.query.filter_by(divisionID=division_id).all()
    request_object["data"] = {}
    request_object["data"]["matches"] = [match.to_json() for match in matches]
    return jsonify(request_object), 200


@matches_blueprint.route('/matches/division/<division_id>/team/<team_id>', methods=['GET'])
def get_matches_from_division_filtered_on_team(division_id, team_id):
    """get matches with from a specific division"""
    request_object = {
        'status': 'failed'
    }
    division = requests.get("http://teamsclubs:5000/divisions/" + str(division_id))
    if not division:
        request_object["message"] = "Division doesn't exist"
        return jsonify(request_object), 404
    matches = Match.query.filter(Match.divisionID == division_id,
                                 or_(Match.awayTeamID == team_id, Match.homeTeamID == team_id)).all()
    request_object["data"] = {}
    request_object["data"]["matches"] = [match.to_json() for match in matches]
    return jsonify(request_object), 200


@matches_blueprint.route('/matches/ranking', methods=['GET'])
def get_division_ranking():
    response_object = {
        "status": "succes"
    }
    divisions = [r[0] for r in Match.query.with_entities(Match.divisionID).distinct()]
    returnObject = {}
    for divisionID in divisions:
        returnObject[divisionID] = {}
        s1 = sqlalchemy.select([Match.homeTeamID.label('id'), func.sum(Match.goalsHome).label('goalsHome')]).where(
            Match.divisionID == divisionID).group_by(Match.homeTeamID).alias("home")
        s2 = sqlalchemy.select([Match.awayTeamID.label('id2'), func.sum(Match.goalsAway).label('goalsAway')]).where(
            Match.divisionID == divisionID).group_by(Match.awayTeamID).alias("away")
        teams = db.session.query(s1.c.id.label('id'), (s2.c.goalsAway + s1.c.goalsHome).label("goals")
                                 ).filter(s1.c.id == s2.c.id2).order_by(desc("goals")).first()
        returnObject[divisionID]["attack"] = teams

        s1 = sqlalchemy.select(
            [Match.homeTeamID.label('id'), func.sum(Match.goalsAway).label('goalsHomeOpponent')]).where(
            Match.divisionID == divisionID).group_by(Match.homeTeamID).alias("home")
        s2 = sqlalchemy.select(
            [Match.awayTeamID.label('id2'), func.sum(Match.goalsHome).label('goalsAwayOpponent')]).where(
            Match.divisionID == divisionID).group_by(Match.awayTeamID).alias("away")
        teams = db.session.query(s1.c.id.label('id'), (s2.c.goalsAwayOpponent + s1.c.goalsHomeOpponent).label("goals")
                                 ).filter(s1.c.id == s2.c.id2).order_by(asc("goals")).first()
        returnObject[divisionID]["defence"] = teams

        s1 = sqlalchemy.select(
            [Match.homeTeamID.label('id'), func.count(Match.homeTeamID).label('amountOfCleanSheetsHome')]).where(
            and_(Match.divisionID == divisionID, Match.goalsHome == 0)).group_by(Match.homeTeamID).alias("home")
        s2 = sqlalchemy.select(
            [Match.awayTeamID.label('id2'), func.count(Match.awayTeamID).label('amountOfCleanSheetsAway')]).where(
            and_(Match.divisionID == divisionID, Match.goalsAway == 0)).group_by(Match.awayTeamID).alias("away")
        teams = db.session.query(s1.c.id.label('id'),
                                 (s2.c.amountOfCleanSheetsAway + s1.c.amountOfCleanSheetsHome).label("CleanSheets")
                                 ).filter(s1.c.id == s2.c.id2).order_by(desc("CleanSheets")).first()
        returnObject[divisionID]["CleanSheets"] = teams

    response_object["data"] = returnObject
    return jsonify(response_object), 200


@matches_blueprint.route('/matches/leagueTable', methods=['GET'])
def get_league_table():
    """Get division tables"""
    request_object = {
        'status': 'failed'
    }
    divisions = {}
    for match in Match.query.filter(Match.date < func.now()).all():
        if match.divisionID not in divisions:
            divisions[match.divisionID] = {}
        if match.homeTeamID not in divisions[match.divisionID]:
            teamInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(match.homeTeamID))
            if teamInfo.status_code != 200:
                request_object["message"] = "couldn't find team info"
                return jsonify(request_object), 404
            divisions[match.divisionID][match.homeTeamID] = {
                'points': 0,
                'wins': 0,
                'loses': 0,
                'draw': 0,
                'played': 0,
                'info': teamInfo.json()["data"]
            }
        if match.awayTeamID not in divisions[match.divisionID]:
            teamInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(match.awayTeamID))
            if teamInfo.status_code != 200:
                request_object["message"] = "couldn't find team info"
                return jsonify(request_object), 404
            divisions[match.divisionID][match.awayTeamID] = {
                'points': 0,
                'wins': 0,
                'loses': 0,
                'draw': 0,
                'played': 0,
                'info': teamInfo.json()["data"]
            }
        divisions[match.divisionID][match.awayTeamID]["played"] = divisions[match.divisionID][match.awayTeamID][
                                                                      "played"] + 1
        divisions[match.divisionID][match.homeTeamID]["played"] = divisions[match.divisionID][match.homeTeamID][
                                                                      "played"] + 1
        divisions[match.divisionID][match.awayTeamID]["points"] = divisions[match.divisionID][match.awayTeamID][
                                                                      "points"] + match.goalsAway
        divisions[match.divisionID][match.homeTeamID]["points"] = divisions[match.divisionID][match.homeTeamID][
                                                                      "points"] + match.goalsHome
        if match.goalsHome > match.goalsAway:
            divisions[match.divisionID][match.homeTeamID]["wins"] = divisions[match.divisionID][match.homeTeamID][
                                                                        "wins"] + 1
            divisions[match.divisionID][match.awayTeamID]["loses"] = divisions[match.divisionID][match.homeTeamID][
                                                                         "loses"] + 1
        elif match.goalsHome == match.goalsAway:
            divisions[match.divisionID][match.homeTeamID]["draw"] = divisions[match.divisionID][match.homeTeamID][
                                                                        "draw"] + 1
            divisions[match.divisionID][match.awayTeamID]["draw"] = divisions[match.divisionID][match.homeTeamID][
                                                                        "draw"] + 1
        else:
            divisions[match.divisionID][match.homeTeamID]["loses"] = divisions[match.divisionID][match.homeTeamID][
                                                                         "loses"] + 1
            divisions[match.divisionID][match.awayTeamID]["wins"] = divisions[match.divisionID][match.homeTeamID][
                                                                        "wins"] + 1
    request_object = {'status': 'success', "data": divisions}
    return jsonify(request_object), 200


@matches_blueprint.route('/compareTeams/<team_A>&<team_B>')
def compareTeams(team_A, team_B):
    request_object = {
        'status': 'failed',
        'message': "request failed\n"
    }
    success = True
    team_A = requests.get("http://teamsclubs:5000/teams/" + str(team_A))
    if team_A.status_code != 200:
        request_object["message"] += "Team A could not be found\n"
        success = False
    team_B = requests.get("http://teamsclubs:5000/teams/" + str(team_B))
    if team_B.status_code != 200:
        request_object["message"] += "Team B could not be found\n"
        success = False
    if success:
        response_object = {}
        response_object["head2headNumber"] = Match.query.filter(and_(
            or_(and_(Match.homeTeamID == team_A.json()["data"]["id"], Match.awayTeamID == team_B.json()["data"]["id"]),
                and_(Match.awayTeamID == team_A.json()["data"]["id"],
                     Match.homeTeamID == team_B.json()["data"]["id"])),
            Match.datetime_as_timestamp < datetime.datetime.now())).count()

        response_object["wins"] = (Match.query.filter(and_(
            or_(and_(Match.homeTeamID == team_A.json()["data"]["id"], Match.awayTeamID == team_B.json()["data"]["id"],
                     Match.goalsHome > Match.goalsAway),
                and_(Match.awayTeamID == team_A.json()["data"]["id"],
                     Match.homeTeamID == team_B.json()["data"]["id"], Match.goalsAway > Match.goalsHome))),
            Match.datetime_as_timestamp < datetime.datetime.now()).count(),
                                   Match.query.filter(and_(
                                       or_(and_(Match.homeTeamID == team_A.json()["data"]["id"],
                                                Match.awayTeamID == team_B.json()["data"]["id"],
                                                Match.goalsHome < Match.goalsAway),
                                           and_(Match.awayTeamID == team_A.json()["data"]["id"],
                                                Match.homeTeamID == team_B.json()["data"]["id"],
                                                Match.goalsAway < Match.goalsHome))),
                                       Match.datetime_as_timestamp < datetime.datetime.now()).count()
                                   )

        response_object["historicalCombined"] = Match.query.with_entities(Match.homeTeamID, Match.goalsHome,
                                                                          Match.goalsAway, Match.awayTeamID).filter(
            and_(
                or_(and_(Match.homeTeamID == team_A.json()["data"]["id"],
                         Match.awayTeamID == team_B.json()["data"]["id"]),
                    and_(Match.awayTeamID == team_A.json()["data"]["id"],
                         Match.homeTeamID == team_B.json()["data"]["id"])),
                Match.datetime_as_timestamp < datetime.datetime.now())).order_by(desc(Match.date),
                                                                                 desc(Match.time)).limit(3).all()

        currentForm = (
        Match.query.with_entities(Match.homeTeamID, Match.goalsHome, Match.goalsAway, Match.awayTeamID, Match.datetime_as_timestamp).filter(
            and_(or_(Match.homeTeamID == team_A.json()["data"]["id"], Match.awayTeamID == team_A.json()["data"]["id"]),
                 Match.datetime_as_timestamp < datetime.datetime.now())).order_by(desc(Match.date)).limit(5).all(),
        Match.query.with_entities(Match.homeTeamID, Match.goalsHome, Match.goalsAway, Match.awayTeamID, Match.datetime_as_timestamp).filter(
            and_(or_(Match.homeTeamID == team_B.json()["data"]["id"], Match.awayTeamID == team_B.json()["data"]["id"]),
                 Match.datetime_as_timestamp < datetime.datetime.now())).order_by(desc(Match.date)).limit(5).all())

        currentFormConverted = [[],[]]
        for match in currentForm[0]:
            winSymbol = ""
            loseSymbol = ""
            if match.homeTeamID == team_A.json()["data"]["id"]:
                winSymbol = "W"
                loseSymbol = "L"
            else:
                winSymbol = "L"
                loseSymbol = "W"

            if match.goalsHome == match.goalsAway:
                currentFormConverted[0].append("D")
            elif match.goalsHome > match.goalsAway:
                currentFormConverted[0].append(winSymbol)
            else:
                currentFormConverted[0].append(loseSymbol)

        for match in currentForm[1]:
            winSymbol = ""
            loseSymbol = ""
            if match.homeTeamID == team_B.json()["data"]["id"]:
                winSymbol = "W"
                loseSymbol = "L"
            else:
                winSymbol = "L"
                loseSymbol = "W"

            if match.goalsHome == match.goalsAway:
                currentFormConverted[1].append("D")
            elif match.goalsHome > match.goalsAway:
                currentFormConverted[1].append(winSymbol)
            else:
                currentFormConverted[1].append(loseSymbol)


        response_object["currentForm"] = currentFormConverted
        request_object["status"] = 'success'
        request_object["data"] = response_object
        return jsonify(request_object), 200
    else:
        return jsonify(request_object), 404


@matches_blueprint.route('/', methods=['GET', 'POST'])
def index():
    pass


@matches_blueprint.route('/matches/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
