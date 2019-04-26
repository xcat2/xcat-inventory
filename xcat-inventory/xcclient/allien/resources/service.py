###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import request, current_app
from flask_restplus import Namespace, Resource, reqparse, fields

from xcclient.xcatd import XCATClient, XCATClientParams

from ..invmanager import get_inventory_by_type, upd_inventory_by_type, transform_from_inv, transform_to_inv
from ..invmanager import InvalidValueException, ParseException
from .inventory import resource

ns = Namespace('manager', description='Manage services and tasks')
srvreq = ns.model('SvrReq', {
    'noderange': fields.String(description='The nodes or groups to be operated', required=True),
    'spec': fields.Raw(description='The specification of operation', required=False)
})


@ns.route('/provision')
class ProvisionResource(Resource):

    @ns.doc('list_provision')
    def get(self):
        """List all provision tasks"""
        # TODO: it should be supported by new install monitor daemon

        # Just return mock data now
        return []

    @ns.expect(srvreq)
    @ns.doc('create_provision')
    def post(self):
        """Create a provision task for nodes"""
        # TODO: Long term, it need a task id for each created provision task
        #       And tracked in the install monitor daemon.

        # Now just invode `rinstall` to xcatd
        data = request.get_json()
        boot_state = data.get('boot_state')
        if data.get('boot_param'):
            current_app.logger.debug("boot_param=%s" % data.get('boot_param'))

        param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
        cl = XCATClient()
        cl.init(current_app.logger, param)

        result = cl.nodeset(noderange=data['noderange'], boot_state=boot_state)
        return dict(outputs=result.output_msgs)

