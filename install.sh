#I don't have a linux system to test this out so if this script doesn't work use these commands seperatly in a terminal

sudo docker-compose -f docker-compose-dev.yml build

sudo docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
sudo docker-compose -f docker-compose-dev.yml run teamsclubs python manage.py recreate-db
sudo docker-compose -f docker-compose-dev.yml run referee python manage.py recreate-db
sudo docker-compose -f docker-compose-dev.yml run matches python manage.py recreate-db

sudo docker-compose -f docker-compose-dev.yml run users python manage.py seed-db
sudo docker-compose -f docker-compose-dev.yml run matches python manage.py seed-db
sudo docker-compose -f docker-compose-dev.yml run teamsclubs python manage.py seed-db
sudo docker-compose -f docker-compose-dev.yml run referee python manage.py seed-db

