###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app
from flask_restplus import Resource, Namespace, fields, reqparse
from xcclient.inventory.manager import export_by_type, importobj

ns = Namespace('inventory', ordered=True, description='Inventory Management')

resource = ns.model('Resource', {
    'meta': fields.Raw(description='The meta info of resource', required=True),
    'spec': fields.Raw(description='The specification of resource', required=False)
})

inv_resource = ns.model('Inventory', {
})


def _split_inventory_types(types):

    include = list()
    exclude = ['credential']

    # get the include and exclude
    for rt in types:
        rt = rt.strip()
        if rt.startswith('-'):
            exclude.append(rt[1:])
        else:
            include.append(rt)

    return include, exclude


@ns.route('/')
class InventoryResource(Resource):

    @ns.doc('export_inventory')
    @ns.param('types', 'exported inventory types')
    def get(self):
        """get all inventory defined in store"""

        parser = reqparse.RequestParser()
        parser.add_argument('types', action='split', help="Exported inventory types, started with '-' means to exclude")
        args = parser.parse_args()

        include = None
        exclude = None
        if args.get('types'):
            include, exclude = _split_inventory_types(args.get('types'))
            if include:
                include = ','.join(include)

        return export_by_type(include, None, destfile=None, destdir=None, fmt='dict', version=None, exclude=exclude)

    @ns.doc('import_inventory')
    @ns.param('types', 'imported inventory types')
    @ns.expect(inv_resource)
    @ns.response(201, 'Inventory successfully imported.')
    def post(self):
        """import inventory objects"""
        data = request.get_json()

        parser = reqparse.RequestParser()
        parser.add_argument('types', action='split', help="Imported inventory types, started with '-' means to exclude")
        parser.add_argument('clean', action='split', help="Imported inventory types, started with '-' means to exclude")
        args = parser.parse_args()

        include = None
        exclude = None
        if args.get('types'):
            include, exclude = _split_inventory_types(args.get('types'))
            if include:
                include = ','.join(include)

        importobj(None, None, include, None, dryrun=False, version=None,
                  update=args.get('clean'), envs=args.get('environs'), env_files=None, exclude=args.exclude.split(','))

        return None, 201

