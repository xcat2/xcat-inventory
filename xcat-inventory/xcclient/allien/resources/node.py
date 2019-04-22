###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import current_app
from flask_restplus import Namespace, Resource, fields, reqparse

from ..invmanager import get_nodes_list, get_node_inventory, get_node_attributes
from xcclient.xcatd import XCATClient, XCATClientParams

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


@ns.route('/nodes')
class NodeListResource(Resource):

    @ns.marshal_list_with(node, skip_none=True)
    def get(self):
        return get_nodes_list().values()

    @ns.doc('create_node')
    def post(self):

        param = XCATClientParams(os.environ.get('XCAT_MASTER'))
        cl = XCATClient()
        cl.init(current_app.logger, param)

        result = cl.mkdef(args=['-t', 'node'])
        return result.output_msgs


@ns.route('/nodes/_detail', '/nodes/<node>/_detail')
class NodeDetailResource(Resource):

    def get(self, node=None):

        if not node:
            return get_nodes_list().values()

        return get_node_attributes(node)


@ns.route('/nodes/_inventory', '/nodes/<node>/_inventory')
class NodeInventoryResource(Resource):

    def get(self, node=None):

        return get_node_inventory('node', node)
