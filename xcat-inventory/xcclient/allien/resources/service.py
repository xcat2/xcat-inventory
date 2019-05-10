###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import request, current_app
from flask_restplus import Namespace, Resource, reqparse, fields

from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from ..srvmanager import provision

ns = Namespace('manager', description='Manage services and tasks')
srvreq = ns.model('SvrReq', {
    'noderange': fields.String(description='The nodes or groups to be operated', required=True),
    'action_spec': fields.Raw(description='The optional parameters of the operation', required=False)
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
        if data.get('action_spec'):
            current_app.logger.debug("action_spec=%s" % data.get('action_spec'))

        try:
            result = provision(data['noderange'], data.get('action_spec'))
        except XCATClientError as e:
            ns.abort(500, str(e))

        # TODO: a reasonable response for each nodes, now just return xcatd output
        return dict(outputs=result)

