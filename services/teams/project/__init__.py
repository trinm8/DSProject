import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(script_info=None):

    app = Flask(__name__)

    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)

    from project.api.teams import teams_blueprint
    from project.api.clubs import clubs_blueprint
    from project.api.divisions import division_blueprint
    app.register_blueprint(teams_blueprint)
    app.register_blueprint(clubs_blueprint)
    app.register_blueprint(division_blueprint)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app