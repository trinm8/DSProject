docker-compose -f docker-compose-dev.yml up -d --build

docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
docker-compose -f docker-compose-dev.yml run teamsclubs python manage.py recreate-db
docker-compose -f docker-compose-dev.yml run referee python manage.py recreate-db
docker-compose -f docker-compose-dev.yml run matches python manage.py recreate-db

docker-compose -f docker-compose-dev.yml run users python manage.py seed-db
docker-compose -f docker-compose-dev.yml run matches python manage.py seed-db
docker-compose -f docker-compose-dev.yml run teamsclubs python manage.py seed-db
docker-compose -f docker-compose-dev.yml run referee python manage.py seed-db

docker-compose -f docker-compose-dev.yml stop

