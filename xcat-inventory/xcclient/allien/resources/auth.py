###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app, make_response, jsonify
from flask_restplus import Resource, Namespace
import uuid
from exceptions import *
from xcclient.xcatd.client.xcat_exceptions import XCATClientError
from ..invmanager import *
from . import auth_request

ns = Namespace('auth', description='The Authorization section for APIs')
@ns.route('/login')
class ToLogin(Resource):

    def get(self, code=200):
        return make_response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''', code)
    def post(self):
        try:
            if request.headers['Content-Type'] == 'application/json':
                post_data = request.get_json()
            elif 'form' in request.headers['Content-Type']:
                post_data = request.form.to_dict()
            else:
                return self.get(400)
        except Exception:
            return ns.abort(400)
        usr = post_data['username']
        pwd = post_data['password']
        if check_user_account(usr, pwd, usertype="xcat-user"): 
            token = uuid.uuid1()
            expire = time.time()
            insert_user_token(usr, str(token), str(expire))
            return jsonify({'token':{'id': str(token), 'expire': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(expire))}}) 
        else:
            return make_response('''
        Login Failed, try again
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''', 401)

@ns.route('/refresh')
class ToRefresh(Resource):
    @auth_request
    def get(self):
        return make_response("Token verification done, succeed")
    def post(self):
        try:
            auth_header = request.headers.get('Authorization')
            auth_token = auth_header.split(" ")[1] 
        except Exception:
            ns.abort(401)
        update_user_token(auth_token, str(time.time()))
        return

@ns.route('/logout')
class ToLogout(Resource):
    @auth_request
    def post(self):
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split(" ")[1] 
        remove_user_token(auth_token)
        return 'Logged out'
