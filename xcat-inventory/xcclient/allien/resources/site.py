###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask_restplus import Namespace, Resource, fields, reqparse
from xcclient.allien.app import dbi
from ..invmanager import get_inventory_by_type

ns = Namespace('globalconf', description='System Level Settings')

site = ns.model('Site', {
    'name': fields.String(required=True, description='The attribute name'),
    'value': fields.String(required=True, description='The attribute value'),
})

site_list = ns.model('Site', {
    'name': fields.String(required=True, description='The attribute name'),
    'value': fields.String(required=True, description='The attribute value'),
})


@ns.route('/sites')
class SitesResource(Resource):

    def get(self):
        return get_inventory_by_type('site')

    @ns.expect(site)
    def post(self):
        pass


@ns.route('/sites/<name>')
@ns.response(404, 'Context not found')
class SiteResource(Resource):
    @ns.doc('list_site')
    @ns.param('attr', 'The site attribute name')
    def get(self, context):
        """List all site attributes"""
        parser = reqparse.RequestParser()
        parser.add_argument('attrs', location='args', action='split', help='Queried attributes')
        args = parser.parse_args()
        # print(args)
        return dbi.gettab(['site'])

    def put(self):
        """Modify site with all attributes"""
        return dbi.gettab(['site'])

    def patch(self):
        """Modify some attributes of site"""
        return dbi.gettab(['site'])


@ns.route('/sites/<name>/attr/<attr>')
@ns.param('name', 'The site context name')
@ns.param('attr', 'The site attribute name')
@ns.response(404, 'Attribute not found')
class SiteAttrResource(Resource):
    @ns.doc('get_site_attr')
    # @ns.marshal_with(site)
    def get(self, attr):
        """Fetch a site attribute given its name"""
        for nv in SITES:
            if attr['name'] == nv:
                return attr['value']
        ns.abort(404)






