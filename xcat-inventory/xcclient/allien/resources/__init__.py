###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-


from flask import Blueprint
from flask_restplus import Resource, Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp, version='1.0', title='xCAT API',
          description='RESTful API of xCAT service',
)
from .node import NodeResource
api.add_resource(NodeResource, '/node')

from .noderange import NodeRangeResource
api.add_resource(NodeRangeResource, '/noderange/<string:nr>')

from .network import NetworkResource
api.add_resource(NetworkResource, '/network')

from .site import ns as api_setting_ns
api.add_namespace(api_setting_ns)

from .nodehm import *
api.add_resource(PowerResource, '/node/<string:id>/power')
api.add_resource(PowerRangeResource, '/power')

from .inventory import *
api.add_resource(InventoryNodeResource, '/inventory/node', '/inventory/node/<string:id>')
