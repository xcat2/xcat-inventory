###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

"""The app module, containing the app factory function."""

import os
import logging
from flask import Flask, Blueprint

from flask_caching import Cache
# from .extensions import bcrypt, cache, db, migrate, jwt, cors
from xcclient.xcatd.client import xcat_log
from xcclient.xcatd.client.xcat_exceptions import XCATClientError
from xcclient.inventory.dbsession import DBsession
from xcclient.inventory.dbfactory import dbfactory
from xcclient.inventory.utils import initglobal
dbsession = DBsession()
dbi = dbfactory(dbsession)

# TODO put this into global config
redis_cli_config = { 'CACHE_TYPE': 'redis', 'CACHE_REDIS_HOST': '127.0.0.1', 'CACHE_REDIS_PORT': 6379, 'CACHE_REDIS_DB': '', 'CACHE_REDIS_PASSWORD': '' }
# redis_cli_config = {'CACHE_TYPE': 'simple'}

cache = Cache(config=redis_cli_config)


class URLSchemeFixMiddleware:
    def __init__(self, application):
        self.app = application

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


def create_app(config_object=None):
    """Application factory"""

    app = Flask(__name__)
    #app = Flask(__name__, static_folder='../../../static', template_folder='../../../templates')
    #app.wsgi_app = URLSchemeFixMiddleware(app.wsgi_app)
    #app.config['SESSION_TYPE'] = 'memcached'
    #app.config['SECRET_KEY'] = 'super secret key for devops'
    #app.permanent_session_lifetime = timedelta(minutes=10)

    app.url_map.strict_slashes = False
    if config_object:
        app.config.from_object(config_object)

    register_logger(app)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    #register_shellcontext(app)
    #register_commands(app)

    # TODO: need a method to monitor the version is changed.
    initglobal()

    @app.route('/ping', methods=['GET'])
    def test():
        return 'pong'

    return app


def register_logger(app):
    app.logger = xcat_log.get_logger()
    # Formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(process)d %(thread)d %(module)s %(message)s')
    if not os.path.isdir('log'):
        os.mkdir('log')
    file_handler = logging.FileHandler('log/xcatapi.log')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)


def register_extensions(app):
    """Register Flask extensions."""
    cache.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""

    from .resources import api_bp
    app.register_blueprint(api_bp)

    #from .view import console_bp
    #app.register_blueprint(console_bp)


def register_errorhandlers(app):

    def errorhandler(error):
        response = error.to_json()
        response.status_code = error.status_code
        return response

    app.errorhandler(XCATClientError)(errorhandler)


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {
        }

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)

