###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import request, current_app
from flask_restplus import Namespace, Resource, fields, reqparse

from xcclient.xcatd import XCATClient, XCATClientParams
from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from ..invmanager import *
from ..srvmanager import provision
from . import auth_request 

ns = Namespace('system', ordered=True, description='System Management')

node = ns.model('Node', {
    'name': fields.String(required=True, description='The node name', attribute=lambda x: x.get('nodelist.node')),
    'groups': fields.String(attribute=lambda x: x.get('nodelist.groups')),
    'status': fields.String(attribute=lambda x: x.get('nodelist.status')),
    'updated_time': fields.String(attribute=lambda x: x.get('nodelist.statustime')),
    'sync_status': fields.String(attribute=lambda x: x.get('nodelist.updatestatus')),
    'sync_updated_time': fields.String(attribute=lambda x: x.get('nodelist.updatestatustime')),
    'app_status': fields.String(attribute=lambda x: x.get('nodelist.appstatus')),
    'app_updated_time': fields.String(attribute=lambda x: x.get('nodelist.appstatustime')),
    'description': fields.String(attribute=lambda x: x.get('nodelist.comments')),
})

actionreq = ns.model('ActionReq', {
    'action': fields.String(description='The specified operation', required=True),
    'action_spec': fields.Raw(description='The optional parameters of the operation', required=False)
})


@ns.route('/nodes')
class NodeListResource(Resource):

    @auth_request
    @ns.doc('list_all_nodes')
    def get(self):
        return get_nodes_list().keys()

    @ns.doc('create_node')
    def post(self):

        param = XCATClientParams(os.environ.get('XCAT_MASTER'))
        cl = XCATClient()
        cl.init(current_app.logger, param)

        result = cl.mkdef(args=['-t', 'node'])
        return result.output_msgs


@ns.route('/nodes/<node>/_status')
class NodeStatusResource(Resource):

    @ns.doc('query node status')
    def get(self, node):

        dataset = get_nodes_status(node)
        if node and not dataset:
            ns.abort(400, "Node '%s' is not found" % node)

        name, status = dataset.popitem()
        spec = transform_to_status(status)

        return dict(meta=dict(name=name), status=spec)


@ns.route('/nodes/_detail', '/nodes/<node>/_detail')
class NodeDetailResource(Resource):

    def get(self, node=None):

        if not node:
            return get_nodes_list().values()

        return get_node_attributes(node)


@ns.route('/nodes/_inventory', '/nodes/<node>/_inventory')
class NodeInventoryResource(Resource):

    @ns.doc('list_nodes_inventory')
    def get(self, node=None):
        """get specified OS image resource"""

        result = get_nodes_inventory('node', node)
        if node:
            if not result:
                ns.abort(404, "Node '%s' is not found." % node)

            return transform_from_inv(result)[0]

        return transform_from_inv(get_nodes_inventory('node', node))


SUPPORTED_OPERATIONS = {
    'rinstall': provision
}


@ns.route('/nodes/<node>/_operation')
class NodeOperationResource(Resource):

    @ns.expect(actionreq)
    @ns.doc('operate_node')
    def post(self, node):
        """Operate a node with specified action"""

        data = request.get_json()
        action = data.get('action')
        if action not in SUPPORTED_OPERATIONS:
            ns.abort(400, 'Not supported operation: %s' % action)

        if data.get('action_spec'):
            current_app.logger.debug("action_spec=%s" % data.get('action_spec'))

        try:
            result = SUPPORTED_OPERATIONS[action](node, data.get('action_spec'))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, str(e))
        except XCATClientError as e:
            ns.abort(500, str(e))

        current_app.logger.debug("outputs=%s" % result)
        return 'Success'
