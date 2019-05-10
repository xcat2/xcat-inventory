###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app
from flask_restplus import Resource, Namespace, fields, reqparse

from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from ..invmanager import get_inventory_by_type, upd_inventory_by_type, del_inventory_by_type, transform_from_inv, transform_to_inv, validate_resource_input_data, patch_inventory_by_type
from ..invmanager import InvalidValueException, ParseException
from .inventory import ns, resource, patch_action

"""
These APIs is to handle networking related resources: subnet, route.
"""


@ns.route('/subnets')
class NetworkListResource(Resource):

    def get(self):
        """get all the networks defined in store"""
        return transform_from_inv(get_inventory_by_type('network'))

    @ns.doc('create_subnet')
    @ns.expect(resource)
    @ns.response(201, 'Subnet successfully created.')
    def post(self):
        """create a network object"""
        data = request.get_json()

        # TODO: better to handle the exceptions
        try:
            upd_inventory_by_type('network', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201


@ns.route('/subnets/<string:name>')
@ns.response(404, 'network not found.')
class NetworkResource(Resource):

    def get(self, name):
        """get a specified network resource"""
        result = get_inventory_by_type('network', [name])
        if not result:
            ns.abort(404)

        return transform_from_inv(result)[-1]

    def delete(self, name):
        """delete a specified network resource"""
        try:
          del_inventory_by_type('network', [name])
        except (XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 200

    @ns.expect(resource)
    def put(self, name):
        """replace a specified network resource"""
        data = request.get_json()
        # TODO, need to check if the name is consistent
        try:
            validate_resource_input_data(data, name)
            upd_inventory_by_type('network', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 200

    @ns.expect(patch_action)
    def patch(self, name):
        """Modify a specified network resources"""
        data = request.get_json()
        try:
            patch_inventory_by_type('network', name, data)
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 201


@ns.route('/routes')
class RoutesListResource(Resource):

    def get(self):
        """get all the routes defined in store"""
        return transform_from_inv(get_inventory_by_type('route'))

    @ns.expect(resource)
    @ns.response(201, 'Route successfully created.')
    def post(self):
        """create a static route """
        data = request.get_json()

        try:
            upd_inventory_by_type('route', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201


@ns.route('/routes/<string:name>')
@ns.response(404, 'Route not found.')
class RouteResource(Resource):

    def get(self, name):
        """get a specified route in store"""
        result = get_inventory_by_type('route', [name])
        if not result:
            ns.abort(404, "Route {} doesn't exist".format(name))

        return transform_from_inv(result)[-1]

    def delete(self, name):
        """delete a specified route """
        try:
            del_inventory_by_type('route', [name])
        except (XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 200

    @ns.expect(resource)
    def put(self, name):
        """replace a specified route """
        data = request.get_json()
        try:
            validate_resource_input_data(data, name)
            upd_inventory_by_type('route', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 200

    @ns.expect(patch_action)
    def patch(self, name):
        """Modify a specified route """
        data = request.get_json()
        try:
            patch_inventory_by_type('route', name, data)
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 201
