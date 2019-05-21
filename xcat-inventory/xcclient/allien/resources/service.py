###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
import time

from flask import request, current_app
from flask_restplus import Namespace, Resource, reqparse, fields

from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from ..srvmanager import provision
from ..resmanager import apply_resource, free_resource, get_occupied_resource, get_free_resource

from . import auth_request, token_parser

ns = Namespace('manager', description='Manage services and tasks')
srvreq = ns.model('SvrReq', {
    'noderange': fields.String(description='The nodes or groups to be operated', required=True),
    'action_spec': fields.Raw(description='The optional parameters of the operation', required=False)
})


@ns.route('/provision')
class ProvisionResource(Resource):

    @auth_request
    @ns.expect(srvreq)
    @ns.param('Authorization', type=str, help="token \<token id\>", location='headers', required=True)
    @ns.doc('create_provision')
    def post(self):
        """Create a provision task for nodes"""
        # TODO: Long term, it need a task id for each created provision task
        #       And tracked in the install monitor daemon.

        # Now just invoke `rinstall` to xcatd
        data = request.get_json()
        if data.get('action_spec'):
            current_app.logger.debug("action_spec=%s" % data.get('action_spec'))

        try:
            result = provision(data['noderange'], data.get('action_spec'))
        except XCATClientError as e:
            ns.abort(500, str(e))

        # TODO: a reasonable response for each nodes, now just return xcatd output
        return dict(outputs=result)


resreq = ns.model('ResReq', {
    'capacity': fields.Integer(description='The required resource count', default=1, required=True),
    'criteria_spec': fields.Raw(description='The criteria specification of the requesting', required=False)
})


@ns.route('/resmgr')
class ResMgrResource(Resource):

    @auth_request
    @ns.expect(token_parser)
    @ns.param('pool', 'show free pool information')
    @ns.doc('get_resource')
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('pool', location='args', help='free pool')
        args = parser.parse_args()
        pool_flag = args.get('pool')

        if pool_flag:
            free = get_free_resource()
            return dict(total=len(free), pool=free)
        else:
            return get_occupied_resource()

    @auth_request
    @ns.expect(resreq)
    @ns.param('Authorization', 'token <token id>')
    @ns.doc('apply_resource')
    def post(self):
        """Apply resources"""

        data = request.get_json()
        criteria = data.get('criteria_spec')
        if criteria:
            current_app.logger.debug("criteria_spec=%s" % criteria)

        # TODO: parse criteria and choose nodes from the free pool

        # Just return mock data now
        return apply_resource(data.get('capacity', 1), criteria=criteria)

    @auth_request
    @ns.expect(token_parser)
    @ns.doc('free_resource')
    @ns.param('name', 'resource name')
    def delete(self):
        """Free resources"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='args', help='resource name')
        args = parser.parse_args()
        node = args.get('name')

        return free_resource(name=node), 200

