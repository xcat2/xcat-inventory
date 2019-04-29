###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
import tempfile

from flask import request, current_app
from flask_restplus import Resource, Namespace, fields, reqparse
from xcclient.inventory.manager import export_by_type, importobj

from ..invmanager import InvalidValueException, split_inventory_types

ns = Namespace('inventory', ordered=True, description='Inventory Management')

resource = ns.model('Resource', {
    'meta': fields.Raw(description='The meta info of resource', required=True),
    'spec': fields.Raw(description='The specification of resource', required=False)
})

inv_resource = ns.model('Inventory', {
})


@ns.route('/')
class InventoryResource(Resource):

    @ns.doc('export_inventory')
    @ns.param('types', 'inventory types for exporting')
    def get(self):
        """get all inventory defined in store"""

        parser = reqparse.RequestParser()
        parser.add_argument('types', action='split', help="inventory types, started with '-' means to exclude")
        args = parser.parse_args()

        include = None
        exclude = None
        try:
            include, exclude = split_inventory_types(args.get('types'))
            if args.get('types'):
                if include:
                    include = ','.join(include)
        except InvalidValueException as e:
            ns.abort(400, e.message)

        return export_by_type(include, None, destfile=None, destdir=None, fmt='dict', version=None, exclude=exclude)

    @ns.doc('import_inventory')
    @ns.param('types', 'inventory types for importing')
    @ns.param('clean', 'clean mode. IF specified, all objects other than the ones to import will be removed.')
    @ns.expect(inv_resource)
    @ns.response(201, 'Inventory successfully imported.')
    def post(self):
        """import inventory objects"""

        # TODO:  need to lock the operation as xcat-inventory will conflict when run it in the mean time.
        parser = reqparse.RequestParser()
        parser.add_argument('types', action='split', help="inventory types, started with '-' means to exclude")
        parser.add_argument('clean', help="clean mode. If specified, all objects other than the ones to import will be removed.")
        args = parser.parse_args()

        include = None
        exclude = None
        try:
            include, exclude = split_inventory_types(args.get('types'))
            if args.get('types'):
                if include:
                    include = ','.join(include)
        except InvalidValueException as e:
            ns.abort(400, e.message)

        data = request.get_data()
        invfile = tempfile.NamedTemporaryFile(delete=False)
        invfile.write(data)
        invfile.close()

        importobj(invfile.name, None, include, None, dryrun=False, version=None,
                  update=args.get('clean'), envs=args.get('environs'), env_files=None, exclude=exclude)
        os.unlink(invfile.name)
        return None, 201

