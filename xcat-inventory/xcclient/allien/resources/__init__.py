###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-


from flask import Blueprint
from flask_restplus import Resource, Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp, version='2.0', title='xCAT API v2', prefix="/v2",
          description='RESTful API of xCAT',
)


from .inventory import ns as api_inv_ns
api.add_namespace(api_inv_ns)

from .node import ns as api_node_ns
api.add_namespace(api_node_ns)

#from .noderange import NodeRangeResource
#api.add_resource(NodeRangeResource, '/noderange/<string:nr>')

from .network import ns as api_net_ns
api.add_namespace(api_net_ns)

from .osimage import ns as api_image_ns
api.add_namespace(api_image_ns)

from .site import ns as api_setting_ns
api.add_namespace(api_setting_ns)

from .security import ns as api_security_ns
api.add_namespace(api_security_ns)

from .service import ns as api_manager_ns
api.add_namespace(api_manager_ns)

#from .nodehm import *
#api.add_resource(PowerResource, '/node/<string:id>/power')
#api.add_resource(PowerRangeResource, '/power')



