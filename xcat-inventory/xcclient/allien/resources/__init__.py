###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-


from flask import Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

from .node import NodeResource
api.add_resource(NodeResource, '/node')

from .network import NetworkResource
api.add_resource(NetworkResource, '/network')

from .site import SiteResource
api.add_resource(SiteResource, '/site')

from .nodehm import PowerResource
api.add_resource(PowerResource, '/nodehm/power')
