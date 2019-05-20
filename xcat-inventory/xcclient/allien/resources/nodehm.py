###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import current_app, request
from flask_restplus import Resource, reqparse
from xcclient.xcatd import XCATClient, XCATClientParams
from xcclient.xcatd.client.xcat_exceptions import XCATClientError
from ..invmanager import InvalidValueException
from .node import ns, actionreq
from .service import ns as ns1
from .service import srvreq

POWER_ACTION=["on","off","state"]

@ns.route('/nodes/<node>/power')
class PowerResource(Resource):
    """power hardware control operation"""

    @ns.expect(actionreq)
    @ns.doc('power_node')
    def post(self, node):
        "power a node with specified action"""
        data = request.get_json()
        action = data.get('action')
        res={}
        if action not in POWER_ACTION:
            ns.abort(400, 'Not supported operation: %s' % action)

        try:
            param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
            cl = XCATClient()
            cl.init(current_app.logger, param)
            result = cl.rpower(node,action)
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))

        res['powerstate']=result.node_dict[node].state
        return res, 200

    def _validator(self, args):
        current_app.logger.info(args)

@ns1.route('/power')
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
