###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-


from flask import Blueprint, request, abort
from flask_restplus import Resource, Api
from functools import wraps
from ..invmanager import check_user_token

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp, version='2.0', title='xCAT API v2', prefix="/v2",
          description='RESTful API of xCAT',
)

def auth_request(function):
    @wraps(function)
    def check_token(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            auth_token = auth_header.split(" ")[1]
        except Exception:
            abort(401)
        #return make_response("Unauthorized requrest, please login first", 401)
        flag = check_user_token(auth_token)
        if flag == 1:
            abort(401, {'message': 'Token expired, pleased refresh or Login again'})
        elif flag == 2:
            abort(401)
        return function(*args, **kwargs)
    return check_token

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

from .auth import ns as api_manager_ns
api.add_namespace(api_manager_ns)

#from .nodehm import *
#api.add_resource(PowerResource, '/node/<string:id>/power')
#api.add_resource(PowerRangeResource, '/power')

