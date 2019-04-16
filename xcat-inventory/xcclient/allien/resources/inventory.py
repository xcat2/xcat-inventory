###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask_restplus import Resource, Namespace, fields
from xcclient.inventory.manager import InventoryFactory, export_by_type
from xcclient.allien.app import dbsession

ns = Namespace('inventory', ordered=True, description='Inventory Management')

resource = ns.model('Resource', {
    'meta': fields.Raw(description='The meta info of resource', required=True),
    'spec': fields.Raw(description='The specification of resource', required=False)
})


@ns.route('/')
class InventoryResource(Resource):

    def get(self):
        """get all inventory defined in store"""
        # TODO, support `fmt` in query parameter
        return export_by_type(None, None, destfile=None, destdir=None, fmt='json', version=None, exclude=['osimage','node'])

    @ns.doc('import_inventory')
    @ns.expect(resource)
    @ns.response(201, 'Inventory successfully imported.')
    def post(self):
        """import inventory objects"""
        data = request.get_json()

        # TODO: call inventory to store in DB

        return None, 201


