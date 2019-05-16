###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
import random
import uuid

from flask import g, current_app

from xcclient.xcatd import XCATClient, XCATClientParams

from .invmanager import get_all_nodes, ParseException


def provision(nr, action_spec=None):
    """Helper method to parse payload and do rintall"""

    boot_state = 'osimage'
    target =  None
    if action_spec:
        if 'osimage' in action_spec and action_spec.get('osimage'):
            target = "osimage=%s" % action_spec['osimage']

        if 'boot_state' in action_spec and target:
            raise ParseException('Do not specify multiple boot target.')
        elif not target:
            target = action_spec.get('boot_state')

    boot_state = target or boot_state
    # TODO: support more args later

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    result = cl.rinstall(noderange=nr, boot_state=boot_state)
    return result.output_msgs


MOCK_FREE_POOL = get_all_nodes()
_applied = dict()


def apply_resource(count, criteria=None, instance=None):
    if not instance:
        instance = str(uuid.uuid1())

    if len(MOCK_FREE_POOL) < count:
        raise Exception("Not enough free resource.")

    _applied[instance] = list()
    for i in range(count):
        index = random.randint(0, len(MOCK_FREE_POOL)-1)
        node = MOCK_FREE_POOL.keys()[index]
        _applied[instance].append(node)

    for node in _applied[instance]:
        del MOCK_FREE_POOL[node]

    return {instance : ','.join(_applied[instance])}


def free_resource(name=None, instance=None):
    if instance:
        for node in _applied[instance]:
            MOCK_FREE_POOL[node] = ""
        del _applied[instance]
    elif name:
        for sid, occupied in _applied.items():
            # just drop the whole list for MOCK as terraform only apply one node
            if name in occupied:
                for node in _applied[instance]:
                    MOCK_FREE_POOL[node] = ""
                del _applied[sid]
                break


def get_free_resource():
    return MOCK_FREE_POOL.keys()


def get_occupied_resource(instance=None):
    if not instance:
        return _applied

    return {instance : ','.join(_applied[instance])}
