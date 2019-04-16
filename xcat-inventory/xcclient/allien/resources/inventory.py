###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask_restplus import Resource, Namespace, fields
from xcclient.inventory.manager import InventoryFactory
from xcclient.allien.app import dbsession

ns = Namespace('inventory', ordered=True, description='Inventory Management')

resource = ns.model('Resource', {
    'meta': fields.Raw(description='The meta info of resource', required=True),
    'spec': fields.Raw(description='The specification of resource', required=False)
})


class InventoryNodeResource(Resource):

    def get(self, id=None):
        hdl = InventoryFactory.createHandler('node', dbsession, None)

        nodelist = []
        if id:
            nodelist.append(id)
        return hdl.exportObjs(nodelist, None, fmt='json')
