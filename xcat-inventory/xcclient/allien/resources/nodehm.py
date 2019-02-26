###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import current_app
from flask_restful import Resource, reqparse
from ..hwmanager import *

class PowerResource(Resource):
    """power hardware control operation"""

    def post(self, id):

        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, location='form')
        args = parser.parse_args()

        self._validator(args)
        # 1, parse node range, and get power, mgmt interface of specified nodes, and categorize them in dict
        nodelist = ['mid05tor12cn01', 'mid05tor12cn02', 'mid05tor12cn03', 'mid05tor12cn04', 'mid05tor12cn05']
        # 2, handle each interface for the nodes in parallel with plugins
        #    - invoke rpc to new hw process (run it directly in api server for temporary)
        #    - socket to xcatd for legacy mode: hmc, ipmi (later will use pyghmi)
        return rpower([id], args.get('action'))

    def _validator(self, args):
        current_app.logger.info(args)


class PowerRangeResource(Resource):

    def post(self):
        # TODO, using marshelmallow to replace RequestParser
        parser = reqparse.RequestParser()
        parser.add_argument('noderange', type=str, location='form')
        parser.add_argument('action', type=str, location='form')
        args = parser.parse_args()

        self._validator(args)
        # 1, parse node range, and get power, mgmt interface of specified nodes, and categorize them in dict
        nodelist = ['mid05tor12cn01', 'mid05tor12cn02', 'mid05tor12cn03', 'mid05tor12cn04', 'mid05tor12cn05']
        # 2, handle each interface for the nodes in parallel with plugins
        #    - invoke rpc to new hw process (run it directly in api server for temporary)
        #    - socket to xcatd for legacy mode: hmc, ipmi (later will use pyghmi)
        return rpower(nodelist, args.get('operation'))

    def _validator(self, args):
        current_app.logger.info(args)
