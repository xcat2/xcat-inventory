###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import request, current_app
from flask_restplus import Namespace, Resource, reqparse

from xcclient.xcatd import XCATClient, XCATClientParams

from ..invmanager import get_inventory_by_type, upd_inventory_by_type, transform_from_inv, transform_to_inv
from ..invmanager import InvalidValueException, ParseException
from .inventory import resource

ns = Namespace('globalconf', description='System Level Settings')

@ns.route('/sites')
class SitesResource(Resource):

    @ns.doc('list_sites')
    def get(self):
        """List all site contexts"""
        return transform_from_inv(get_inventory_by_type('site'))

@ns.route('/sites/<string:context>')
@ns.response(404, 'Context not found')
class SiteResource(Resource):

    @ns.doc('get_site')
    @ns.param('attrs', 'Site attribute names')
    def get(self, context):
        """Get the attributes of specified context ( only 'clustersite' allowed now )"""

        parser = reqparse.RequestParser()
        parser.add_argument('attrs', location='args', action='split', help='Queried attributes')
        args = parser.parse_args()

        result = get_inventory_by_type('site', [context])
        if not result:
            ns.abort(404)

        if not args.get('attrs'):
            return transform_from_inv(result)[-1]

        site_obj = result.get(context)
        temp_spec = {}
        for attr in args.get('attrs'):
           temp_spec[attr] = site_obj.get(attr)

        return {'meta': {'name':context}, 'spec':temp_spec}

    @ns.expect(resource)
    def put(self, context):
        """Replace site context with all attributes"""

        data = request.get_json()

        # TODO: better to handle the exceptions
        try:
            upd_inventory_by_type('site', transform_to_inv(data), clean=True)
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201

    def patch(self, context):
        """Modify attributes of a site context"""

        data = request.get_json()

        # TODO: better to handle the exceptions
        try:
            upd_inventory_by_type('site', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201


@ns.route('/sites/<context>/<attr>')
@ns.param('context', 'The site context name')
@ns.param('attr', 'The site attribute name')
@ns.response(404, 'Attribute not found')
class SiteAttrResource(Resource):

    @ns.doc('get_site_attr')
    def get(self, context, attr):
        """Fetch a site attribute by the given name"""

        result = get_inventory_by_type('site', [context])
        if not result:
            ns.abort(404, 'Context not found')

        site_obj = result.get(context)
        if attr not in site_obj:
            ns.abort(404, 'Attribute not found')

        return {attr: site_obj.get(attr)}

    @ns.doc('set_site_attr')
    @ns.response(400, 'Must specify the value in query parameter.')
    def post(self, context, attr):
        """Set a site attribute by the given name"""

        if "clustersite" != context:
            ns.abort(404, 'Context not found')

        parser = reqparse.RequestParser()
        parser.add_argument('value', location='args', help='Value to be set on the attribute')
        args = parser.parse_args()

        if not args.get('value'):
            ns.abort(400, 'Context not found')

        param = XCATClientParams(os.environ.get('XCAT_SERVER'))
        cl = XCATClient()
        cl.init(current_app.logger, param)

        result = cl.chdef(args=['-t', 'site', '-o', context, "%s=%s" % (attr, args.get('value'))])
        return result.output_msgs

    @ns.doc('delete_site_attr')
    def delete(self, context, attr):
        """Delete a site attribute by the given name"""

        if "clustersite" != context:
            ns.abort(404, 'Context not found')

        param = XCATClientParams(os.environ.get('XCAT_SERVER'))
        cl = XCATClient()
        cl.init(current_app.logger, param)

        result = cl.chdef(args=['-t', 'site', '-o', context, "%s=" % (attr, )])
        return result.output_msgs
