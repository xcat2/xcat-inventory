###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask_restplus import Namespace, Resource, fields, reqparse
from xcclient.allien.app import dbi

#from . import api
ns = Namespace('globalconf', description='System Level Settings')

site = ns.model('Site', {
    'name': fields.String(required=True, description='The attribute name'),
    'value': fields.String(required=True, description='The attribute value'),
})

site_list = ns.model('Site', {
    'name': fields.String(required=True, description='The attribute name'),
    'value': fields.String(required=True, description='The attribute value'),
})

#########################################
# Mock data for site
SITES = [
    {'master': '10.1.1.101', 'domain': 'example.com'},
]
#########################################


@ns.route('/site')
class SiteResource(Resource):
    @ns.doc('list_site')
    @ns.param('attr', 'The site attribute name')
    def get(self):
        '''List all site attributes'''
        parser = reqparse.RequestParser()
        parser.add_argument('attrs', location='args', action='split', help='Queried attributes')
        args = parser.parse_args()
        print(args)
        return dbi.gettab(['site'])

    def put(self):
        '''Modify site with all attributes'''
        return dbi.gettab(['site'])

    def patch(self):
        '''Modify some attributes of site'''
        return dbi.gettab(['site'])


@ns.route('/site/<attr>')
@ns.param('attr', 'The site attribute name')
@ns.response(404, 'Attribute not found')
class SiteAttr(Resource):
    @ns.doc('get_site_attr')
    #@ns.marshal_with(site)
    def get(self, attr):
        '''Fetch a site attribute given its name'''
        for nv in SITES:
            if attr['name'] == nv:
                return attr['value']
        ns.abort(404)

@ns.route('/secrets')
class SecretsResource(Resource):
    @ns.doc('list_secrets')
    def get(self):
        '''List all secrets objects'''
        return dbi.gettab(['passwd'])




