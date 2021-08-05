from flask import Blueprint, jsonify, request, render_template, flash, abort, redirect, url_for

from project.forms.fixtureForm import filterFixtureByDivision
from project.forms.teamsForm import teamsSearchForm, editTeamInfo
from project.forms.LoginForm import LoginForm

from project.decorators import login_required

import requests, datetime

ui_blueprint = Blueprint('UI', __name__, template_folder='./templates')

@ui_blueprint.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404



def convertMatchTimeStrToDateTime(date, time):
    matchDate = datetime.datetime.combine(datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").date(),
                                          datetime.datetime.strptime(time, "%H:%M:%S").time())
    return matchDate

@ui_blueprint.route('/', methods=['GET'])
def index():
    return render_template('home.html')


@ui_blueprint.route('/LeagueTables', methods=['GET'])
def leagueTables():
    table = {}
    divisions = requests.get("http://teamsclubs:5000/divisions")
    if divisions.status_code == 200:
        for division in divisions.json()["data"]["divisions"]:
            table[division["id"]] = {
                'id': division["id"],
                'name': division["name"],
                'teams': []
            }
        matches = requests.get("http://matches:5000/matches/leagueTable")
        if matches.status_code != 200:
            print(matches.json()["message"])
            return render_template('leagueTables.html', divisions=None)
        for key, value in matches.json()["data"].items():
            table[int(key)]["teams"].append(value)
        return render_template('leagueTables.html', divisions=divisions.json()["data"]["divisions"], matches=matches.json()["data"],
                               table=table)
    else:
        return render_template('leagueTables.html', divisions=None)


@ui_blueprint.route('/fixtures', methods=['GET', 'POST'])
def fixtures():
    form = filterFixtureByDivision(request.form)
    if form.validate_on_submit():
        fixtures = {}
        if form.teamID.data or form.teamID.data == 0:
            team = requests.get("http://teamsclubs:5000/teams/" + str(form.teamID.data))
            if team.status_code != 200:
                flash(team.json()["message"], 'error')
                return render_template('fixtures.html', form=form)
            matches = requests.get("http://matches:5000/matches/division/" + str(form.divisionID.data) + "/team/" + str(form.teamID.data))
        else:
            matches = requests.get("http://matches:5000/matches/division/" + str(form.divisionID.data))
        if matches.status_code == 404:
            flash(matches.json()["message"], 'error')
            return render_template('fixtures.html', form=form)

        teamInfo = {}

        for match in matches.json()["data"]["matches"]:
            for id in [match["homeTeamID"], match["awayTeamID"]]:
                if id not in teamInfo:
                    name = requests.get("http://teamsclubs:5000/teamInfo/" + str(id))
                    if name.status_code == 200:
                        teamInfo[id] = name.json()["data"]


        for match in matches.json()["data"]["matches"]:
            match["homeTeam"] = teamInfo[match["homeTeamID"]]
            match["awayTeam"] = teamInfo[match["awayTeamID"]]
            if datetime.datetime.strptime(match["date"], "%a, %d %b %Y %H:%M:%S %Z") not in fixtures:
                fixtures[datetime.datetime.strptime(match["date"], "%a, %d %b %Y %H:%M:%S %Z")] = {
                    "matches": [match]
                }
            else:
                fixtures[datetime.datetime.strptime(match["date"], "%a, %d %b %Y %H:%M:%S %Z")]["matches"].append(match)
            matchDate = datetime.datetime.combine(datetime.datetime.strptime(match["date"], "%a, %d %b %Y %H:%M:%S %Z").date(), datetime.datetime.strptime(match["time"], "%H:%M:%S").time())
            if matchDate > datetime.datetime.now():
                match["result"] = match["time"]
                fixtures[datetime.datetime.strptime(match["date"], "%a, %d %b %Y %H:%M:%S %Z")]["passed"] = False
            else:
                match["result"] = str(match["goalsHome"]) + " - " + str(match["goalsAway"])
                fixtures[datetime.datetime.strptime(match["date"], "%a, %d %b %Y %H:%M:%S %Z")]["passed"] = True
        convertedFixtures = []
        for key, value in fixtures.items():
            convertedFixtures.append((key, value))
        convertedFixtures.sort(key=lambda x: x[0], reverse=True)

        return render_template('fixtures.html', form=form, fixtures=convertedFixtures)
    return render_template('fixtures.html', form=form)


@ui_blueprint.route('/divisionRankings', methods=['GET'])
def division_rankings():
    divisions = requests.get("http://matches:5000/matches/ranking")
    if divisions.status_code == 200:
        divisions = divisions.json()["data"]
        for divisionID, division in divisions.items():
            for result in division.values():
                name = requests.get(str("http://teamsclubs:5000/teamInfo/" + str(result[0])))
                if name.status_code == 200:
                    result[0] = name.json()["data"]["name"]
            divisionName = requests.get("http://teamsclubs:5000/divisions/"+str(divisionID))
            division["name"] = divisionName.json()["data"]["name"]
        return render_template('divisionRankings.html', divisions=divisions)
    return render_template('divisionRankings.html')


@ui_blueprint.route('/fixture/<match_id>', methods=['GET'])
def specific_fixture(match_id):
    resultObject = {}
    specificMatch = requests.get("http://matches:5000/matches/" + str(match_id))
    if specificMatch.status_code == 200:

        homeInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(specificMatch.json()["data"]["homeTeamID"]))
        if homeInfo.status_code == 200:
            resultObject["TeamA"] = homeInfo.json()["data"]
            teamAid = homeInfo.json()["data"]["id"]
        else:
            abort(404)

        awayInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(specificMatch.json()["data"]["awayTeamID"]))
        if awayInfo.status_code == 200:
            resultObject["TeamB"] = awayInfo.json()["data"]
            teamBid = awayInfo.json()["data"]["id"]
        else:
            abort(404)

        resultObject["date"] = datetime.datetime.strptime(specificMatch.json()["data"]["date"], "%a, %d %b %Y %H:%M:%S %Z").strftime("%d-%m-%Y")
        resultObject["time"] = specificMatch.json()["data"]["time"]
        referee = "No referee assigned"
        if specificMatch.json()["data"]["refereeID"]:
            refereeResponse = requests.get("http://referee:5000/referee/" + str(specificMatch.json()["data"]["refereeID"]))
            if refereeResponse.status_code == 200:
                referee = refereeResponse.json()["data"]["first_name"] + " " + refereeResponse.json()["data"]["last_name"]
        resultObject["referee"] = referee
        matchdate = convertMatchTimeStrToDateTime(specificMatch.json()["data"]["date"], specificMatch.json()["data"]["time"])
        if matchdate > datetime.datetime.now():
            comparingData = requests.get("http://matches:5000/compareTeams/" + str(specificMatch.json()["data"]["homeTeamID"]) + '&' + str(specificMatch.json()["data"]["awayTeamID"]))
            if comparingData.status_code == 200:
                resultObject["head2headNumber"] = comparingData.json()["data"]["head2headNumber"]
                resultObject["head2headWins"] = comparingData.json()["data"]["wins"]
                historical = comparingData.json()["data"]["historicalCombined"]

                teamIDs = {}

                for game in historical:
                    if game[0] == teamAid:
                        game[0] = resultObject["TeamA"]["name"]
                    elif game[0] == teamBid:
                        game[0] = resultObject["TeamA"]["name"]
                    else:
                        if game[0] in teamIDs:
                            game[0] = teamIDs[game[0]]
                        newTeam = requests.get("http://teamclubs:5000/teamInfo/" + str(game[0]))
                        if newTeam.status_code == 200:
                            teamIDs[game[0]] = newTeam.json()["data"]["name"]
                            game[0] = newTeam.json()["data"]["name"]
                        else:
                            game[0] = "Team not found, id:" + str(game[0])

                    if game[-1] == teamAid:
                        game[-1] = resultObject["TeamA"]["name"]
                    elif game[-1] == teamBid:
                        game[-1] = resultObject["TeamB"]["name"]
                    else:
                        if game[-1] in teamIDs:
                            game[-1] = teamIDs[game[-1]]
                        newTeam = requests.get("http://teamclubs:5000/teamInfo/" + str(game[-1]))
                        if newTeam.status_code == 200:
                            teamIDs[game[-1]] = newTeam.json()["data"]["name"]
                            game[-1] = newTeam.json()["data"]["name"]
                        else:
                            game[-1] = "Team not found, id:" + str(game[-1])
                resultObject["historical"] = historical
                resultObject["currentForm"] = comparingData.json()["data"]["currentForm"]
        if matchdate > datetime.datetime.now() and matchdate < datetime.datetime.now() + datetime.timedelta(days=7):
            days = ((datetime.datetime.now() + datetime.timedelta(days=7)) - matchdate).days
            weather = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=0&lon=0&units=metric&exclude=current,minutely,hourly&appid=60c17e865997f70b0eafb801886a4af6")
            if weather.status_code == 200:
                weatherdata = weather.json()
                resultObject["weather"] = weatherdata["daily"][days]
        return render_template('individualFixture.html', fixture=resultObject)
    return render_template('individualFixture.html', message=specificMatch)

@ui_blueprint.route('/teams/', methods=['GET', 'POST'])
def team_search():
    form = teamsSearchForm(request.form)
    teams = requests.get("http://teamsclubs:5000/teams")
    if teams.status_code == 200:
        teams = teams.json()["data"]["teams"]
        for i in range(len(teams)):
            info = requests.get("http://teamsclubs:5000/teamInfo/" + str(teams[i]["id"]))
            if info.status_code == 200:
                teams[i] = info.json()["data"]
    else:
        teams = []
    if form.validate_on_submit():
        return redirect(str(form.data["teamID"]))
    return render_template('teamSearch.html', form=form, teams=teams)


@ui_blueprint.route('/teams/<team_id>', methods=['GET'])
def teamPage(team_id):
    info = requests.get("http://teamsclubs:5000/teamInfo/" + str(team_id))
    if info.status_code == 200:

        upcomingMatches = requests.get("http://matches:5000/matches/upcoming/" + str(team_id))
        previousMatches = requests.get("http://matches:5000/matches/previous/" + str(team_id))
        if upcomingMatches.status_code != 200 and previousMatches.status_code != 200:
            abort(404)
        return render_template('teamPage.html', info=info.json()["data"], upcomingMatches=upcomingMatches.json()["data"],
                               previousMatches=previousMatches.json()["data"])
    else:
        abort(404)
        return render_template('teamPage.html')

@ui_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.cookies.get('username'):
        loginData = {
            'username': str(request.cookies.get('username')),
            'password': str(request.cookies.get('password'))
        }
        loginAttempt = requests.post('http://users:5000/users/authenticate', json=loginData)
        if loginAttempt.status_code == 200:
            return redirect("loginPortal")
    loginForm = LoginForm(request.form)
    if loginForm.validate_on_submit():
        loginData = {
                    'username': str(loginForm.username.data),
                    'password': str(loginForm.password.data)
                     }
        loginAttempt = requests.post('http://users:5000/users/authenticate', json=loginData)
        if loginAttempt.status_code == 200:
            response = redirect("../loginPortal")
            response.set_cookie('username', loginAttempt.json()["data"]["username"])
            response.set_cookie('password', loginAttempt.json()["data"]["password"])
            response.set_cookie('id', loginAttempt.json()["data"]["id"])
            return response
        elif loginAttempt.status_code == 404 or loginAttempt.status_code == 403:
            flash(loginAttempt.json()["message"], 'error')
            return render_template("login.html", form=loginForm, message=loginAttempt.json()["message"])
        else:
            print("test")
    return render_template("login.html", form=loginForm)

@ui_blueprint.route('/loginPortal', methods=['GET', 'POST'])
@login_required
def loginPortal():
    return render_template("loginPortal.html")

@ui_blueprint.route('/')
@login_required
def editTeam():
    editform = editTeamInfo(request.form)

    pass