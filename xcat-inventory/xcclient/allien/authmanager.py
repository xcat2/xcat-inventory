###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from .app import dbi
import time


def check_user_account(username, password):
    usertypes = ['xcat', 'xcat-user']
    dataset = dbi.gettab(['passwd'], usertypes)
    for usertype in usertypes:
        v = dataset[usertype]
        if type(v) is list:
            for entry in v:
                if entry['passwd.username'] == username and entry['passwd.password'] == password:
                    return True
        elif v['passwd.username'] == username and v['passwd.password'] == password:
                return True
    return False


def check_user_token(token_string, username=None, check_expire=True):
    dataset = dbi.gettab(['token'], [token_string])
    if dataset:
        exp = dataset[token_string]['token.expire']
        usr = dataset[token_string]['token.username']
        if not username is None and usr != username:
            return 2, None
        if not check_expire or time.time() >= float(exp):
            return 0, usr
        else:
            return 1, None
    return 2, None


def insert_user_token(username, tokenid, expire):
    dbi.addtabentries('token', {'tokenid': tokenid, 'username': username, 'expire': expire})
    dbi.commit()
     

def update_user_token(tokenid, expire):
    dbi.updatetabentries('token', {'tokenid': tokenid, 'expire': expire})
    dbi.commit()


def remove_user_token(tokenid):
    dbi.deltabentries('token', {'tokenid': tokenid})
    dbi.commit()
