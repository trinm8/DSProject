from flask import Blueprint, request, render_template, flash, abort, redirect, jsonify

from project.forms.fixtureForm import filterFixtureByDivision, editHomeScores
from project.forms.teamsForm import teamsSearchForm, editTeamInfo
from project.forms.LoginForm import LoginForm

from project.api.decorators import login_required

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
    try:
        divisions = requests.get("http://teamsclubs:5000/divisions")
    except requests.exceptions.ConnectionError:
        return render_template('leagueTables.html', divisions=None)
    if divisions.status_code == 200:
        for division in divisions.json()["data"]["divisions"]:
            table[division["id"]] = {
                'id': division["id"],
                'name': division["name"],
                'teams': []
            }
        try:
            matches = requests.get("http://matches:5000/matches/leagueTable")
        except requests.exceptions.ConnectionError:
            return render_template('leagueTables.html', divisions=None)
        else:
            if matches.status_code != 200:
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
            try:
                matches = requests.get("http://matches:5000/matches/division/" + str(form.divisionID.data) + "/team/" + str(form.teamID.data))
            except requests.exceptions.ConnectionError:
                return render_template('fixtures.html', form=form)
        else:
            try:
                matches = requests.get("http://matches:5000/matches/division/" + str(form.divisionID.data))
            except requests.exceptions.ConnectionError:
                return render_template('fixtures.html', form=form)
        if matches.status_code == 404:
            flash(matches.json()["message"], 'error')
            return render_template('fixtures.html', form=form)

        teamInfo = {}
        connectionfailed = False
        for match in matches.json()["data"]["matches"]:
            for id in [match["homeTeamID"], match["awayTeamID"]]:
                if id not in teamInfo:
                    if connectionfailed:
                        teamInfo[id] = None
                        continue
                    try:
                        name = requests.get("http://teamsclubs:5000/teamInfo/" + str(id))
                        if name.status_code == 200:
                            teamInfo[id] = name.json()["data"]
                    except requests.exceptions.ConnectionError:
                        teamInfo[id] = None
                        connectionfailed = True

        for match in matches.json()["data"]["matches"]:
            if teamInfo[match["homeTeamID"]]:
                match["homeTeam"] = teamInfo[match["homeTeamID"]]
            else:
                match["homeTeam"] = None

            if teamInfo[match["awayTeamID"]]:
                match["awayTeam"] = teamInfo[match["awayTeamID"]]
            else:
                match["awayTeam"] = None
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
    try:
        divisions = requests.get("http://matches:5000/matches/ranking")
    except requests.exceptions.ConnectionError:
        return render_template('divisionRankings.html')
    if divisions.status_code == 200:
        finishedProperly = True
        connectionFailedTeams, connectionFailedDivisions = False, False
        divisions = divisions.json()["data"]
        print(divisions)

        for divisionID, division in divisions.items():
            for result in division.values():
                if result is None:
                    continue

                if connectionFailedTeams:
                    result[0] = "Team with ID: " + str(result[0])
                    continue
                try:
                    name = requests.get(str("http://teamsclubs:5000/teamInfo/" + str(result[0])))
                    if name.status_code == 200:
                        result[0] = name.json()["data"]["name"]
                    else:
                        result[0] = "Team with ID: " + str(result[0])
                        finishedProperly = False
                except requests.exceptions.ConnectionError:
                    result[0] = "Team with ID: " + str(result[0])
                    finishedProperly = False
                    connectionFailedTeams = True
            if connectionFailedDivisions:
                division["name"] = "Division with ID: " + divisionID
                finishedProperly = False
                connectionFailedDivisions = True
                continue

            try:
                divisionName = requests.get("http://teamsclubs:5000/divisions/"+str(divisionID))
                if divisionName.status_code == 200:
                    division["name"] = divisionName.json()["data"]["name"]
                else:
                    division["name"] = "Division with ID: " + divisionID
                    finishedProperly = False
            except:
                division["name"] = "Division with ID: " + divisionID
                finishedProperly = False
                connectionFailedDivisions = True
        if not finishedProperly:
            flash("Something went wrong with fetching the data. Resulting data might be substituted with IDs", 'error')
        return render_template('divisionRankings.html', divisions=divisions)
    return render_template('divisionRankings.html')


@ui_blueprint.route('/fixture/<match_id>', methods=['GET'])
def specific_fixture(match_id):
    resultObject = {}

    """Get the data on the specific match"""

    try:
        specificMatch = requests.get("http://matches:5000/matches/" + str(match_id))
    except requests.exceptions.ConnectionError:
        flash("Something went wrong please try again later", 'error')
        return render_template('individualFixture.html')
    if specificMatch.status_code == 200:

        """Get the data on the specific teams. if the requests fail then the ID is used instead"""

        try:
            homeInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(specificMatch.json()["data"]["homeTeamID"]))
            if homeInfo.status_code == 200:
                resultObject["TeamA"] = homeInfo.json()["data"]
                teamAid = homeInfo.json()["data"]["id"]
            else:
                resultObject["TeamA"] = {
                    "name": "Team with ID: " + str(specificMatch.json()["data"]["homeTeamID"])
                }
                teamAid = specificMatch.json()["data"]["homeTeamID"]
                flash("Team A (ID:" + str(specificMatch.json()["data"]["homeTeamID"]) + ") " +
                      "does not exist in the database. Resulting data might thus be incomplete", 'error')
        except requests.exceptions.ConnectionError:
            resultObject["TeamA"] = {
                "name": "Team with ID: " + str(specificMatch.json()["data"]["homeTeamID"])
            }
            teamAid = specificMatch.json()["data"]["homeTeamID"]
            flash("Team A (ID:" + str(specificMatch.json()["data"]["homeTeamID"]) + ") " +
                  "does not exist in the database. Resulting data might thus be incomplete", 'error')

        try:
            awayInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(specificMatch.json()["data"]["awayTeamID"]))
            if awayInfo.status_code == 200:
                resultObject["TeamB"] = awayInfo.json()["data"]
                teamBid = awayInfo.json()["data"]["id"]
            else:
                resultObject["TeamB"] = {
                    "name": "Team with ID: " + str(specificMatch.json()["data"]["awayTeamID"])
                }
                teamBid = specificMatch.json()["data"]["awayTeamID"]
                flash("Team B (ID:" + str(specificMatch.json()["data"]["awayTeamID"]) + ") " +
                      "does not exist in the database. Resulting data might thus be incomplete", 'error')
        except requests.exceptions.ConnectionError:
            resultObject["TeamB"] = {
                "name": "Team with ID: " + str(specificMatch.json()["data"]["awayTeamID"])
            }
            teamBid = specificMatch.json()["data"]["awayTeamID"]
            flash("Team B (ID:" + str(specificMatch.json()["data"]["awayTeamID"]) + ") " +
                  "does not exist in the database. Resulting data might thus be incomplete", 'error')

        """Get the date and time of the match and put it in a correct and workable format"""

        resultObject["date"] = datetime.datetime.strptime(specificMatch.json()["data"]["date"], "%a, %d %b %Y %H:%M:%S %Z").strftime("%d-%m-%Y")
        resultObject["time"] = specificMatch.json()["data"]["time"]

        """Get the assigned referee"""

        referee = "No referee assigned"
        if specificMatch.json()["data"]["refereeID"]:
            try:
                refereeResponse = requests.get("http://referee:5000/referee/" + str(specificMatch.json()["data"]["refereeID"]))
                if refereeResponse.status_code == 200:
                    referee = refereeResponse.json()["data"]["first_name"] + " " + refereeResponse.json()["data"]["last_name"]
            except requests.exceptions.ConnectionError:
                pass
        resultObject["referee"] = referee

        """Check if the match still has to be played and if so construct the data for the webpage"""

        matchdate = convertMatchTimeStrToDateTime(specificMatch.json()["data"]["date"], specificMatch.json()["data"]["time"])
        if matchdate > datetime.datetime.now():
            try:
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
                            game[0] = resultObject["TeamB"]["name"]
                        else:
                            if game[0] in teamIDs:
                                game[0] = teamIDs[game[0]]
                            try:
                                newTeam = requests.get("http://teamclubs:5000/teamInfo/" + str(game[0]))
                                if newTeam.status_code == 200:
                                    teamIDs[game[0]] = newTeam.json()["data"]["name"]
                                    game[0] = newTeam.json()["data"]["name"]
                                else:
                                    game[0] = "Team not found, id:" + str(game[0])
                            except requests.exceptions.ConnectionError:
                                game[0] = "Team not found, id:" + str(game[0])

                        if game[-1] == teamAid:
                            game[-1] = resultObject["TeamA"]["name"]
                        elif game[-1] == teamBid:
                            game[-1] = resultObject["TeamB"]["name"]
                        else:
                            if game[-1] in teamIDs:
                                game[-1] = teamIDs[game[-1]]
                            try:
                                newTeam = requests.get("http://teamclubs:5000/teamInfo/" + str(game[-1]))
                                if newTeam.status_code == 200:
                                    teamIDs[game[-1]] = newTeam.json()["data"]["name"]
                                    game[-1] = newTeam.json()["data"]["name"]
                                else:
                                    game[-1] = "Team not found, id:" + str(game[-1])
                            except requests.exceptions.ConnectionError:
                                game[-1] = "Team not found, id:" + str(game[-1])
                    resultObject["historical"] = historical
                    resultObject["currentForm"] = comparingData.json()["data"]["currentForm"]
            except requests.exceptions.ConnectionError:
                pass

        """Check if the weather for the match if it is upcomming"""

        if matchdate > datetime.datetime.now() and matchdate < datetime.datetime.now() + datetime.timedelta(days=7):
            days = (matchdate - (datetime.datetime.now())).days
            try:
                weather = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=51.2194&lon=4.4025&units=metric&exclude=current,minutely,hourly&appid=60c17e865997f70b0eafb801886a4af6")
                if weather.status_code == 200:
                    weatherdata = weather.json()
                    resultObject["weather"] = weatherdata["daily"][days]
            except requests.exceptions.ConnectionError:
                pass
        return render_template('individualFixture.html', fixture=resultObject)
    return render_template('individualFixture.html', message=specificMatch)

@ui_blueprint.route('/teams/', methods=['GET', 'POST'])
def team_search():
    form = teamsSearchForm(request.form)
    connectionFailed = False
    try:
        teams = requests.get("http://teamsclubs:5000/teams")
    except requests.exceptions.ConnectionError:
        return render_template('teamSearch.html', form=form)
    if teams.status_code == 200:
        teams = teams.json()["data"]["teams"]
        connectionFailed = False
        for i in range(len(teams)):
            if connectionFailed:
                teams.pop(i)
                continue
            try:
                info = requests.get("http://teamsclubs:5000/teamInfo/" + str(teams[i]["id"]))
                if info.status_code == 200:
                    teams[i] = info.json()["data"]
            except requests.exceptions.ConnectionError:
                teams.pop(i)
                connectionFailed = True
    else:
        teams = []
    if form.validate_on_submit():
        return redirect(str(form.data["teamID"]))
    return render_template('teamSearch.html', form=form, teams=teams)


@ui_blueprint.route('/teams/<team_id>', methods=['GET'])
def teamPage(team_id):
    try:
        info = requests.get("http://teamsclubs:5000/teamInfo/" + str(team_id))
    except:
        abort(404)

    if info.status_code == 200:
        try:
            upcomingMatches = requests.get("http://matches:5000/matches/upcoming/" + str(team_id))
            previousMatches = requests.get("http://matches:5000/matches/previous/" + str(team_id))
            if upcomingMatches.status_code != 200:
                upcomingMatches = None
            if previousMatches.status_code != 200:
                previousMatches = None
            return render_template('teamPage.html', info=info.json()["data"], upcomingMatches=upcomingMatches.json()["data"],
                                   previousMatches=previousMatches.json()["data"])
        except requests.exceptions.ConnectionError:
            return render_template('teamPage.html', info=info.json()["data"])
    else:
        abort(404)
        return render_template('teamPage.html')

@ui_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    try:
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
                response.set_cookie('id', str(loginAttempt.json()["data"]["id"]))
                return response
            elif loginAttempt.status_code == 404 or loginAttempt.status_code == 403:
                flash(loginAttempt.json()["message"], 'error')
                return render_template("login.html", form=loginForm, message=loginAttempt.json()["message"])
            else:
                flash(loginAttempt.json()["message"], 'error')
                return render_template("login.html", form=loginForm, message=loginAttempt.json()["message"])
        return render_template("login.html", form=loginForm)
    except requests.exceptions.ConnectionError:
        abort(503)

@ui_blueprint.route('/loginPortal', methods=['GET', 'POST'])
@login_required
def loginPortal():
    try:
        user = requests.get("http://users:5000/users/" + str(request.cookies.get('id')))
        if user.status_code == 200 and user.json()["data"]["admin"] == True:
            return render_template("loginPortal.html", admin=True)
        return render_template("loginPortal.html", admin=False)
    except requests.exceptions.ConnectionError as e:
        abort(503)

@ui_blueprint.route('/editTeam', methods=['GET', 'POST'])
@login_required
def editTeam():
    editform = editTeamInfo(request.form)
    if editform.validate_on_submit():
        changedData = request.form.to_dict()
        requests.put("http://teamsclubs:5000/teams/", json=changedData)
        requests.put("http://teamsclubs:5000/clubs/", json=changedData)
        return redirect("teams/" + str(editform.id.data) )

    userID = request.cookies.get('id')
    userInfo = requests.get("http://users:5000/users/" + str(userID))
    if userInfo.status_code != 200:
        abort(404)
    try:
        teamInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(userInfo.json()["data"]["team"]))
        if teamInfo.status_code != 200:
            flash("Team either doesn't exist or user isn't linked to a team yet.", 'error')
            return redirect("loginPortal")
    except requests.exceptions.ConnectionError:
        flash("Something went wrong on our end please try again later.", 'error')
        return redirect("loginPortal")

    teamInfo = teamInfo.json()["data"]
    editform.suffix = teamInfo["suffix"]
    editform.colors = teamInfo["colors"]
    editform.city = teamInfo["city"]
    editform.zipcode = teamInfo["zipcode"]
    editform.address = teamInfo["address"]
    editform.name = teamInfo["name"]
    editform.id = teamInfo["id"]
    editform.stam_nummer = teamInfo["stam_nummer"]

    return render_template("teamPage.html", info=teamInfo, editMode=True, form=editform)

@ui_blueprint.route('/editScores', methods=['GET', 'POST'])
@login_required
def editScores():
    if request.method == 'POST':
        submittedForm = editHomeScores()

        if submittedForm.validate_on_submit():
            recievedForm = request.form.to_dict()
            requests.put("http://matches:5000/matches", json=recievedForm)
            flash("Match Updated!")
            return redirect("/editScores")
        return redirect("/editScores")

    userID = request.cookies.get('id')
    userInfo = requests.get("http://users:5000/users/" + str(userID))
    if userInfo.status_code != 200:
        abort(404)

    try:
        previousMatches = requests.get("http://matches:5000/matches/PlayedHomeGames/" + str(userInfo.json()["data"]["team"]))
        if previousMatches.status_code != 200:
            flash("The team linked to your account doesn't exist in our database, please contact a administrator.", 'error')
            return redirect("loginPortal")
    except requests.exceptions.ConnectionError:
        flash("Something went wrong on our end please try again later.", 'error')
        return redirect("loginPortal")

    forms = []
    validConnection = True
    for match in previousMatches.json()["data"]:
        if not validConnection:
            forms.append(editHomeScores(matchID=match[0]))
            continue
        try:
            opposingTeamInfo = requests.get("http://teamsclubs:5000/teamInfo/" + str(match[2]))
            if opposingTeamInfo.status_code == 200:
                forms.append(editHomeScores(matchID=match[0],opposingTeamName=opposingTeamInfo.json()["data"]["name"]))
            else:
                forms.append(editHomeScores(matchID=match[0]))
        except requests.exceptions.ConnectionError:
            forms.append(editHomeScores(matchID=match[0]))
            validConnection = False


    #return jsonify(previousMatches.json()["data"])
    return render_template("editHomeScores.html", forms=forms, matches=previousMatches.json()["data"])
