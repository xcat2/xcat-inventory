###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app
from flask_restplus import Resource, Namespace, fields, reqparse

from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from ..invmanager import *
from .inventory import ns, inv_resource, patch_action

"""
These APIs is to handle security related resources: Password, Policy, Zone, Credential.
"""

ns = Namespace('security', description='Security Settings')


@ns.route('/secrets')
class SecretsResource(Resource):

    def get(self):
        """get specified user resource"""
        result = get_inventory_by_type('passwd')
        if not result:
            ns.abort(404)

        return result

    def delete(self):
        """delete a user object"""
        parser = reqparse.RequestParser()
        parser.add_argument('type', location='args', help='secret type')
        parser.add_argument('name', location='args', help='secret account name')
        args = parser.parse_args()
        del_inventory_by_type('passwd', ["%s.%s" % (args.type, args.name)])

    @ns.expect(inv_resource)
    def post(self):
        """create or modify a user object"""
        data = request.get_json()

        try:
            upd_inventory_by_type('passwd', data)
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 200


@ns.route('/policy')
class PolicyResource(Resource):

    @ns.doc('list_policy_rules')
    def get(self):
        """get policy rules"""
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args', action='split', help='policy ID')
        args = parser.parse_args()

        return transform_from_inv(get_inventory_by_type('policy', args.get('id')))

    @ns.doc('create_policy_rule')
    @ns.response(201, 'Policy rule successfully created.')
    @ns.expect(inv_resource)
    def post(self):
        """create or modify a policy object"""
        data = request.get_json()

        try:
            upd_inventory_by_type('policy', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 200

@ns.route('/policy/<string:ruleid>')
class PolicyRuleResource(Resource):

    def get(self, ruleid):
        """get specified policy rule"""

        result = get_inventory_by_type('policy', [ruleid])
        if not result:
            ns.abort(404)

        return transform_from_inv(result)[-1]

    def delete(self, ruleid):
        """delete a policy object"""
        try:
            del_inventory_by_type('policy', [ruleid])
        except XCATClientError as e:
            ns.abort(400, str(e))

        return None, 200

    @ns.expect(inv_resource)
    def put(self, ruleid):
        """replace a policy rule object"""
        data = request.get_json()
        try:
            validate_resource_input_data(data, ruleid)
            upd_inventory_by_type('policy', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201

    @ns.expect(patch_action)
    def patch(self, ruleid):
        """Modify a policy rule object"""
        data = request.get_json()
        try:
            patch_inventory_by_type('policy', ruleid, data)
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 201