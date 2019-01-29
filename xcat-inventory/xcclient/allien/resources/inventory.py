###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import current_app
from flask_restful import Resource
from xcclient.inventory.manager import InventoryFactory
from xcclient.allien.app import dbsession


class InventoryNodeResource(Resource):

    def get(self, id=None):
        hdl = InventoryFactory.createHandler('node', dbsession, None)

        nodelist = []
        if id:
            nodelist.append(id)
        return hdl.exportObjs(nodelist, None, fmt='json')
