###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import request, current_app, make_response, jsonify
from flask_restplus import Resource
import uuid
from functools import wraps
from exceptions import *
from xcclient.xcatd.client.xcat_exceptions import XCATClientError
from ..invmanager import *
"""
These APIs is to handle user login, checking related operations.
"""

def auth_request(function):
    @wraps(function)
    def check_token(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            return make_response("Unauthorized requrest, please login first")
        flag = check_user_token(auth_token)
        if flag == 2:
            return make_response("Unauthorized requrest, please login first")
        elif flag == 1:
            return make_response("Expired, please refresh")
        return function(*args, **kwargs)
    return check_token

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
        if request.headers['Content-Type'] == 'application/json':
            post_data = request.get_json()
        elif 'form' in request.headers['Content-Type']:
            post_data = request.form.to_dict()
        else:
            return self.get(401)
        usr = post_data['username']
        pwd = post_data['password']
        if check_user_account(usr, pwd, usertype="xcat-user"): 
            token = uuid.uuid1()
            insert_user_token(usr, token, time.time())
            return jsonify(token) 
        else:
            return make_response('''
        Login Failed, try again
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''', 401)
class ToRefresh(Resource):
    @auth_request
    def get(self):
        print(request.headers.get('Authorization')) 
        print(request)
        pass
    def post(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1] 
        else:
            return make_response("Unauthorized requrest, please login first")
        update_usertoken(auth_token, time.time())
        return

class ToLogout(Resource):
    def get(self):
        flask_login.logout_user()
        return 'Logged out'
