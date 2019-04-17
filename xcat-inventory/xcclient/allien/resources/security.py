###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app
from flask_restplus import Resource, Namespace, fields, reqparse
from ..invmanager import get_inventory_by_type, upd_inventory_by_type, del_inventory_by_type, transform_from_inv, transform_to_inv
from ..invmanager import InvalidValueException, ParseException
from .inventory import ns, resource

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

    def get(self):
        """get policy"""
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args', action='split', help='policy ID')
        args = parser.parse_args()

        result = get_inventory_by_type('policy', args.get('id'))
        if not result:
            ns.abort(404)

        return result

    def delete(self):
        """delete a policy object"""
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args', action='split', help='policy ID')
        args = parser.parse_args()
        wants = args.get('id')
        if wants:
            wants = args.get(id).split(',')
            del_inventory_by_type('policy', wants)
        else:
            ns.abort(400, "Not allow to delete all policy rules")

    def post(self):
        """create or modify a policy object"""
        data = request.get_json()

        try:
            upd_inventory_by_type('policy', data)
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 200