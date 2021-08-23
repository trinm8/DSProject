# DSProject
## Architecture
![alt text](https://github.com/trinm8/DSProject/blob/main/img/Architecture.png?raw=true)  
 The architecture of my services might look a bit like a mess in this graph but its pretty straightforward. At the top we have the UI service which handles the rendering of the templates and sending out the requests to make sure the right data is shown. Following that we have the "middle" layer which handles the different components of the site, these are mainly a communication layer between the front end service and the individual services. For example, if we would like to see a page with all the matches in our database, the UI service would send out a request to our matches service who will then on his turn send out a request to the matches database. This data will then travel back up the chain until its rendered by the UI service. These middle services might sometimes process this data on their own to satisfy the recieved request, for example when we ask the matches request for the division rankings it will prepare a ranking in advance rather then just giving the raw data of all the played matches and making the UI service figure it all out. The middle layer services also sometimes communicates between themselves, this is mostly to validate recieved data i.e. checking if a recieved ID is valid or not. The only exception to this is the CRUD operations in the admin interface which communicates directly with the database services with flask-admin. The login authentication is done in the users service. 
 
### Design Choises
The main reason why everything is structured like this is because I followed the tutorial given to us and extended that structure throughtout the project. This also why the referee service is so isolated from the rest because I set it up at the beginning but ended up never really using it. The databases are again sepaterated because of the tutorial but are indexed like this because in the assignment the databese entries were listed in this order so I decided to do it like that aswell and add attributes where I needed them. I think another big eye catcher is the direct connection between the UI service and the databases, again this is because I made my admin interface and the CRUD operations using the flask-admin library which requires an SQLAlchemy session with the databases to work properly. As said before the authentication is done in the user service, it is done by simply storing the login information of the user in a cookie which is checked everytime a call is made where a login is requested. It is checked by sending the login credentials obtained from the cookie to the users service which will validate it and then send a response which will say if they were valid or not.
This is a very simple method (and probably not very secure) but I felt like it was good enough for the scope of this project. 

## End points
Alot of the services have a ping endpoint which is another left over of the tutorial we were given, it can be used to test if a service is up or not.

### Matches
- /matches [GET]
  - Takes a GET request. Will return a JSON object with all the data of the matches in the database.
- /matches [POST]
  - Takes a POST request with the data to add a new match to the database. If the data is valid the service will add it to the database and return a respone telling that everything went well. If the data is invalid it will return a response telling what went wrong instead.
- /matches [PUT]
  - Takes a PUT request with the data to update a match score in the database. If the data is valid the service will update the database and return a respone telling that everything went well. If the data is invalid it will return a response telling whats wrong instead.
- /matches/<match_id> [GET]
  - Takes a GET request with a match id of the requested match. If the data is valid the service will return a JSON object with the match data and a message saying that everything went well. If the id is invalid it will return a response saying what went wrong instead.
- /matches/division/<division_id> [GET]
  - Takes a GET request with a division id of the matches we want. If the id is valid a list of matches with the corresponding division id will be returned. if not the response will containt a message informing what went wrong.
- /matches/division/<division_id>/team/<team_id> [GET]
  - Takes both a division and team ID. If these are valid will return a JSON object containing all the matches played by that team in the given division.
- /matches/ranking [GET]
  - Returns a JSON object containing the rankings of each division. The JSON object contain a list of objects which have following data, each contains the id of the team and the amount of the given data:
    - The team with the most goals
    - The team with the least amount of goals scored against them
    - The team with the most clean sheets
- /matches/leagueTable [GET]
  - Returns a JSON object that contains a list of objects each representing a seperate division. Each entry contains the wins, loses, draws, number of matches played, points and the info of a team that division
- /compareTeams/<team_A>&<team_B> [GET]
  - Returns a JSON object with statistics that compare team A and B against eachother. 
- /matches/upcoming/<team_id> [GET]
  - Returns JSON object that contains up to 5 matches upcomming matches for a given team.
- /matches/previous/<team_id> [GET]
  - Returns JSON object with the last 3 matches a given team has played
- /matches/PlayedHomeGames/<team_id> [GET]
  - Returns JSON object with all the matches a given team has played on their home field.
- /matches/assignedReferees?date=\<date> [GET]
  - Returns a list of id of referees that are assigned to any match on the given date.
- /matches/ping [GET]
  - Returns a JSON containing "pong"

### Users
- /users [GET]
  - returns a JSON object with all the users in the database
- /users [POST]
  - Takes the arguments: username, email, password, team, admin and superAdmin in a post request and adds that user to the database
- /users/<user_id> [GET]
  - Returns a JSON object with info about the given user ID.
- /users/authenticate [POST]
  - Takes login credentials from a post request and checks if they are valid. If they are valid returns a success response, if not a message will be returned explaining what went wrong.
- /matches/ping [GET]
  - Returns a JSON containing "pong"

### Teams
- /teams [GET] 
  - Returns a JSON object containing all the teams.
- /teams [POST]
  - takes a post request with the id, stam_nummer, suffix and colors of the new team and adds it to the database.
- /teams [PUT]
  - takes all the data in a put request and updates the corresponding object in the database
- /teams/<team_id> [GET]
  - returns a JSON object with the data of a single team
- /teamInfo/<team_id> [GET]
  - returns the info (i.e. id, stam_nummer, suffix, colors, name, address, zipcode, city, website) of a given team ID

### Divisions
- /divisions [GET]  
  - returns a JSON object with all the divisions
- /divisions [POST]
  - takes a post request with the id_division and name of a new divisions and adds it to the database
- /divisions/<division_id> [GET]
  - takes a division id and returns a JSON object with the data of this object.

### Clubs
- /clubs [GET]
  - Returns a JSON object with all the clubs
- /clubs [POST]
  - takes a post request with the stam_nummer, name, address, zipcode, city and website of a new club and adds it to the database
- /clubs/<stam_nr> [GET]
  - returns the details of a given club.
- /clubs [PUT]
  - takes a put request with the stam_nummer, name, address, zipcode, city and website of a new club and updates the corrisponding object in the database

### UI
- / [GET]
  - returns the homepage of the site
- /LeagueTables [GET]
  - returns the page with the league tables.
- /fixtures [GET, POST]
  - A list of fixtures, is filtered on divisions and optionally on teams
- /divisionRankings [GET]
  - returns the page for the division rankings
- /fixture/<match_id> [GET]
  - returns the page of the given fixture.
- /teams [GET, POST]
  - returns a page with all the teams and has a search bar for team ids
- /teams/<team_id> [GET]
  - returns a page with details of the specified team
- /login [GET, POST]
  - returns a login page, if the person is already logged in then it will automatically redirect to the login portal.
- /loginPortal [GET, POST]
  - returns a page with buttons to the specific account functions
- /editTeam [GET, POST]
  - returns a page where the user can edit the information of their club
- /editScores [GET, POST]
  - returns a page where the user can edit the scores of games played on their home field
