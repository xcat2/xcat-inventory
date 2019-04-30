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

sec_resource = ns.model('Resource', {
    'id': fields.String(description='The ID of Secret'),
    'kind': fields.String(description='The kind of Secrets', required=True),
    'spec': fields.Raw(description='The specification of resource', required=True)
})


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


def _policy_from_inv(obj_d):
    """transform the inventory object model(dict for collection) to a policy rule list"""
    assert obj_d is not None
    assert type(obj_d) is dict

    results = list()
    while len(obj_d) > 0:
        name, spec = obj_d.popitem()
        spec['priority'] = name
        rd = dict(id=name, kind='policy', spec=spec)
        results.append(rd)

    return results

def _policy_to_inv(obj_d):
    """transform the REST object(list or dict) to policy inventory object model(dict for collection)"""
    assert obj_d is not None
    assert type(obj_d) in [dict, list]

    def _dict_to_inv(src):
        assert 'spec' in src
        val = obj_d.get('spec')
        if 'priority' in val:
            name = val.pop('priority')
        else:
            name = obj_d.get('id')

        assert name is not None
        return name, val

    result = dict()
    if type(obj_d) is dict:
        n, v = _dict_to_inv(obj_d)
        result[n] = v
    else:
        # Then it could be a list
        for ob in obj_d:
            n, v = _dict_to_inv(ob)
            result[n] = v
    return result

@ns.route('/policy')
class PolicyResource(Resource):

    @ns.doc('list_policy_rules')
    @ns.param('id', 'Policy rule ids')
    def get(self):
        """get policy rules"""
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args', action='split', help='policy ID')
        args = parser.parse_args()

        return _policy_from_inv(get_inventory_by_type('policy', args.get('id')))

    @ns.doc('create_policy_rule')
    @ns.response(201, 'Policy rule successfully created.')
    @ns.expect(sec_resource)
    def post(self):
        """create or modify a policy object"""
        data = request.get_json()

        # TODO, more input checking
        try:
            if not data.get('spec'):
                raise InvalidValueException("No (spec) section to specify the resource attributes")

            if data.get('kind') and 'policy' != data.get('kind'):
                raise InvalidValueException("Wrong kind is specified")

            name = data['spec'].get('priority') or data.get('id')
            if not name:
                raise InvalidValueException("Priority of the rule is mandatory")

            upd_inventory_by_type('policy', _policy_to_inv(data))

        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 200

@ns.route('/policy/<string:id>')
class PolicyRuleResource(Resource):

    def get(self, id):
        """get specified policy rule"""

        result = get_inventory_by_type('policy', [id])
        if not result:
            ns.abort(404)

        return _policy_from_inv(result)[-1]

    def delete(self, id):
        """delete a policy object"""
        try:
            del_inventory_by_type('policy', [id])
        except XCATClientError as e:
            ns.abort(400, str(e))

        return None, 200

    @ns.expect(sec_resource)
    def post(self, id):
        """modify a policy rule object"""
        data = request.get_json()
        try:

            if not data.get('spec'):
                raise InvalidValueException("No (spec) section to specify the resource attributes")

            if data.get('kind') and 'policy' != data.get('kind'):
                raise InvalidValueException("Wrong kind is specified")

            name = data['spec'].get('priority') or data.get('id')
            if not name:
                raise InvalidValueException("Priority of the rule is mandatory")

            upd_inventory_by_type('policy', _policy_to_inv(data))

        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201

