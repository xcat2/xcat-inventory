###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
import os
from flask import request, current_app
from flask_restplus import Resource, Namespace, fields, reqparse
from xcclient.xcatd import XCATClient, XCATClientParams
from xcclient.xcatd.client.xcat_exceptions import XCATClientError
from ..invmanager import get_inventory_by_type, upd_inventory_by_type, del_inventory_by_type, transform_from_inv, transform_to_inv, validate_resource_input_data, patch_inventory_by_type
from ..invmanager import InvalidValueException, ParseException
from .inventory import ns, resource

"""
These APIs is to handle Image related resources: osimage, osdistro,.
"""

patch_action = ns.model('modify', {
    'modify': fields.Raw(description='The update attr and value info of resource', required=True)
})


@ns.route('/osimages')
class OSimageListResource(Resource):

    def get(self):
        """get OS image list defined in store"""
        return transform_from_inv(get_inventory_by_type('osimage'))

    @ns.doc('create_osimage')
    @ns.expect(resource)
    @ns.response(201, 'OSimage successfully created.')
    def post(self):
        """create an OS image object"""
        data = request.get_json()

        # TODO: better to handle the exceptions
        try:
            validate_resource_input_data(data)
            upd_inventory_by_type('osimage', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201

@ns.route('/osimages/<string:name>')
@ns.response(404, 'OSimage not found.')
class OSimageResource(Resource):

    def get(self, name):
        """get specified OS image resource"""
        result = get_inventory_by_type('osimage', [name])
        if not result:
            ns.abort(404)

        return transform_from_inv(result)[-1]

    def delete(self, name):
        """delete an OS image object"""
        try:
            del_inventory_by_type('osimage', [name])
        except (XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 200

    @ns.expect(resource)
    def put(self, name):
        """replace an OS image object"""
        data = request.get_json()
        try:
            validate_resource_input_data(data, name)
            upd_inventory_by_type('osimage', transform_to_inv(data))
        except (InvalidValueException, ParseException) as e:
            ns.abort(400, e.message)

        return None, 201

    @ns.expect(patch_action)
    def patch(self, name):
        """Modify an OS image object"""
        data = request.get_json()
        try:
            patch_inventory_by_type('osimage', name, data) 
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))

        return None, 201


@ns.route('/distros')
class DistroListResource(Resource):

    def get(self):
        """get distro list defined in store"""
        return transform_from_inv(get_inventory_by_type('osdistro'))

    @ns.doc('create_distro')
    @ns.param('location', 'Image names')
    @ns.response(201, 'Distro successfully created.')
    def post(self):
        """create a distro object"""
        try:
            # TODO: This should do copycds: uploading (if client side), return osdirtro object and osimage links
            parser = reqparse.RequestParser()
            parser.add_argument('location', location='args', action='split', help='Queried image location')
            args = parser.parse_args()
            locations=[]
            locations=args.get('location')
            if not locations:
                ns.abort(400, 'Image not found')

            param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
            cl = XCATClient()
            cl.init(current_app.logger, param)
             
            result = cl.copycds(args=locations)
        except (InvalidValueException, XCATClientError) as e:
            ns.abort(400, str(e))
        return None, 201
    
@ns.route('/distros/<string:name>')
@ns.response(404, 'Distro not found.')
class DistroResource(Resource):

    def get(self, name):
        """get specified distro resource"""
        result = get_inventory_by_type('osdistro', [name])
        if not result:
            ns.abort(404)

        return transform_from_inv(result)[-1]

    def delete(self, name):
        """delete a distro object"""
        # TODO, need to trigger xcatd to clean the ISO directory
        del_inventory_by_type('osdistro', [name])
