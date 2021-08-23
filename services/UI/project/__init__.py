import os

from flask import Flask
from flask_admin import Admin
from flask_admin.menu import MenuLink
from project.api.adminViews import ModelViewAuthorized, ModelViewAuthorizedSuperAdmin, ModelViewAuthorizedMatches
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()


def create_app(script_info=None):

    app = Flask(__name__)
    app.jinja_env.filters['zip'] = zip

    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    try:
        admin = Admin(app, template_mode='bootstrap3')
        matchesEngine = create_engine("postgres://postgres:postgres@matches-db:5432/matches_dev", pool_pre_ping=True)
        teamsEngine = create_engine("postgres://postgres:postgres@teamsclubs-db:5432/teams_dev", pool_pre_ping=True)
        userEngine = create_engine("postgres://postgres:postgres@users-db:5432/users_dev", pool_pre_ping=True)
        refereeEngine = create_engine("postgres://postgres:postgres@referees-db:5432/referees_dev", pool_pre_ping=True)

        meta_dataMatches = MetaData(bind=matchesEngine, reflect=True)
        matches = Table('match', meta_dataMatches, autoload_with=matchesEngine)

        meta_dataTeams = MetaData(bind=teamsEngine, reflect=True)
        teams = Table('teams', meta_dataTeams, autoload_with=teamsEngine)
        clubs = Table('clubs', meta_dataTeams, autoload_with=teamsEngine)
        division = Table('divisions', meta_dataTeams, autoload_with=teamsEngine)

        meta_dataUsers = MetaData(bind=userEngine, reflect=True)
        users = Table('users', meta_dataUsers, autoload_with=userEngine)

        meta_dataReferees = MetaData(bind=refereeEngine, reflect=True)
        referees = Table('referees', meta_dataReferees, autoload_with=refereeEngine)

        Base = declarative_base()
        class Matches(Base):
            __table__ = Table('match', meta_dataMatches, autoload_with=matchesEngine)

        class Teams(Base):
            __table__ = Table('teams', meta_dataTeams, autoload_with=teamsEngine)

        class Clubs(Base):
            __table__ = Table('clubs', meta_dataTeams, autoload_with=teamsEngine)

        class Division(Base):
            __table__ = Table('divisions', meta_dataTeams, autoload_with=teamsEngine)

        class Users(Base):
            __table__ = Table('users', meta_dataUsers, autoload_with=userEngine)

        class Referees(Base):
            __table__ = Table('referees', meta_dataReferees, autoload_with=refereeEngine)

        session = sessionmaker(binds={
            matches: matchesEngine,
            teams: teamsEngine,
            clubs: teamsEngine,
            division: teamsEngine,
            users: userEngine,
            referees: refereeEngine
        })

        finalSession = flask_scoped_session(session, app)

        teamsEngine.execute("SELECT setval('teams_id_seq', (SELECT MAX(id) FROM teams));")
        teamsEngine.execute("SELECT setval('divisions_id_division_seq', (SELECT MAX(id_division) FROM divisions));")

        admin.add_view(ModelViewAuthorizedMatches(Matches, finalSession))
        admin.add_view(ModelViewAuthorized(Teams, finalSession, category="Teams"))
        admin.add_view(ModelViewAuthorized(Clubs, finalSession, category="Teams"))
        admin.add_view(ModelViewAuthorized(Division, finalSession, category="Teams"))
        admin.add_view(ModelViewAuthorized(Referees, finalSession))
        admin.add_view(ModelViewAuthorizedSuperAdmin(Users, finalSession))

        admin.add_link(MenuLink(name="Home Page", category='', url='/'))
    except Exception:
        pass


    db.init_app(app)

    from project.api.main import ui_blueprint
    app.register_blueprint(ui_blueprint)

    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app
