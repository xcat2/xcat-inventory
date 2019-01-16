###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

"""The app module, containing the app factory function."""
from flask import Flask, Blueprint
from flask_restful import Api, Resource
#from .extensions import bcrypt, cache, db, migrate, jwt, cors

from xcclient.inventory.dbsession import DBsession
from xcclient.inventory.dbfactory import dbfactory
dbsession = DBsession()
dbi = dbfactory(dbsession)

def create_app(config_object=None):
    """Application factory"""

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    if config_object:
        app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)
    #register_errorhandlers(app)
    #register_shellcontext(app)
    #register_commands(app)

    @app.route('/ping', methods=['GET'])
    def test():
        return 'pong'

    return app

def register_extensions(app):
    """Register Flask extensions."""
    pass


def register_blueprints(app):
    """Register Flask blueprints."""

    from .resources import api_bp
    app.register_blueprint(api_bp)

def register_errorhandlers(app):

    def errorhandler(error):
        response = error.to_json()
        response.status_code = error.status_code
        return response

    app.errorhandler(InvalidUsage)(errorhandler)


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': user.models.User,
            'UserProfile': profile.models.UserProfile,
            'Article': articles.models.Article,
            'Tag': articles.models.Tags,
            'Comment': articles.models.Comment,
        }

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
