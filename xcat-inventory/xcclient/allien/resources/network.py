###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request
from flask_restplus import Resource, Namespace
from ..invmanager import get_inventory_by_type, upd_inventory_by_type, transform_inv

ns = Namespace('net', ordered=True, description='Networking Management')


@ns.route('/subnets')
class NetworkListResource(Resource):

    def get(self):
        """get networks defined in store"""
        return get_inventory_by_type('network')

    def post(self):
        """create a network object"""
        data = request.get_json()
        upd_inventory_by_type('network', data)


@ns.route('/subnets/_bulk')
class NetworkListResource(Resource):

    def get(self):
        """get networks defined in store"""
        return get_inventory_by_type('network')

    def post(self):
        """bulk delete network object"""
        pass


@ns.route('/subnets/<net>')
class NetworkResource(Resource):

    def get(self, net):
        """get specified network resource"""
        result = get_inventory_by_type('network', [net])
        if not result:
            ns.abort(404)

        return transform_inv(result)

    def delete(self, net):
        pass

    def patch(self, net):
        pass

    def put(self, net):
        pass


@ns.route('/routes')
class RouterListResource(Resource):

    def get(self):
        """get routes defined in store"""
        return get_inventory_by_type('route')

    def post(self):
        """create a static route object"""
        data = request.get_json()
        upd_inventory_by_type('route', data)

