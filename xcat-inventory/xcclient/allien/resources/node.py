###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app
from flask_restplus import Namespace, Resource, fields, reqparse

from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from ..invmanager import *
from ..srvmanager import provision

from . import auth_request, token_parser
from .inventory import resource, patch_action

ns = Namespace('system', ordered=True, description='System Management')

actionreq = ns.model('ActionReq', {
    'action': fields.String(description='The specified operation', required=True),
    'action_spec': fields.Raw(description='The optional parameters of the operation', required=False)
})


@ns.route('/nodes')
class NodeListResource(Resource):
    
    @ns.doc('list_all_nodes')
    @ns.param('type', 'kind of content: name, inventory, status')
    @ns.expect(token_parser)
    @auth_request
    def get(self):
        """get nodes information"""

        parser = reqparse.RequestParser()
        parser.add_argument('type', location='args', help='content type')
        args = parser.parse_args()

        kind = args.get('type') or 'name'
        if kind == 'inventory':
            return transform_from_inv(get_nodes_inventory('node'))
        elif kind == 'status':
            result = list()
            dataset = get_nodes_status()
            for name, status in dataset.items():
                spec = transform_to_status(status)

                result.append(dict(meta=dict(name=name), status=spec))
            return result
        else:
            return get_nodes_list().keys()

    @ns.doc('create_node')
    @ns.expect(resource)
    @ns.response(201, 'Node successfully created.')
    def post(self):
        """create a node object"""
        data = request.get_json()

        try:
            validate_resource_input_data(data)
            upd_inventory_by_type('node', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201


@ns.route('/nodes/<name>')
class NodeInventoryResource(Resource):

    @ns.doc('get_node_inventory')
    def get(self, name):
        """get specified node resource"""

        result = get_nodes_inventory('node', name)

        if not result:
            ns.abort(404, "Node '%s' is not found." % name)

        return transform_from_inv(result)[0]

    @ns.doc('delete_node_inventory')
    def delete(self, name):
        """delete a node object"""
        try:
            del_inventory_by_type('node', [name])
        except XCATClientError as e:
            ns.abort(400, str(e))

        return None, 200

    @ns.expect(resource)
    def put(self, name):
        """replace a node object"""
        data = request.get_json()
        try:
            validate_resource_input_data(data, name)
            upd_inventory_by_type('node', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201

    @ns.expect(patch_action)
    def patch(self, name):
        """Modify a node object"""
        data = request.get_json()
        try:
            patch_inventory_by_type('node', name, data)
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 201


@ns.route('/nodes/<node>/_status')
class NodeStatusResource(Resource):

    @ns.doc('query node status')
    def get(self, node):

        dataset = get_nodes_status(node)
        if not dataset:
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


SUPPORTED_OPERATIONS = {
    'rinstall': provision
}


@ns.route('/nodes/<node>/_operation')
class NodeOperationResource(Resource):

    @ns.expect(token_parser)
    @ns.expect(actionreq)
    @ns.doc('operate_node')
    @auth_request
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
