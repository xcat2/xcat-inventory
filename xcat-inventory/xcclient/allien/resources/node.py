###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import current_app
from flask_restful import Resource
from xcclient.xcatd import XCATClient, XCATClientParams


class NodeResource(Resource):

    def get(self):
        param = XCATClientParams(os.environ.get('XCAT_MASTER'))
        cl = XCATClient()
        cl.init(current_app.logger, param)

        result = cl.lsdef(args=['-t', 'node'])
        return result.output_msgs
