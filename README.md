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

- /matches [POST]
  - Takes a POST request with the data to add a new match to the database. If the data is valid the service will add it to the database and return a respone telling that everything went well. If the data is invalid it will return a response telling what went wrong instead.
- /matches [PUT]
  - Takes a PUT request with the data to update a match score in the database. If the data is valid the service will update the database and return a respone telling that everything went well. If the data is invalid it will return a response telling whats wrong instead.
- /matches/<match_id> [GET]
  - Takes a GET request with a match id of the requested match. If the data is valid the service will return a JSON object with the match data and a message saying that everything went well. If the id is invalid it will return a response saying what went wrong instead.
- /matches [GET]
  - Takes a GET request. Will return a JSON object with all the data of the matches in the database.
