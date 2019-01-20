###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask_restful import Resource
from xcclient.allien.app import dbi

class PowerResource(Resource):
    """power hardware control operation"""

    def post(self):
        # 1, parse node range, and get power, mgmt interface of specified nodes, and categorize them in dict

        # 2, handle each interface for the nodes in parallel
        #    - invoke rpc to new hw process (run it directly in api server for temporary)
        #    - socket to xcatd for legacy mode: hmc, ipmi (later will use pyghmi)
        return dbi.gettab(['nodehm'])

