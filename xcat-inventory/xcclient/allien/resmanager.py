###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
import random
import uuid

from flask import g, current_app
from werkzeug.exceptions import BadRequest

from xcclient.xcatd import XCATClient, XCATClientParams
from xcclient.xcatd.client.xcat_exceptions import XCATClientError

from .invmanager import get_nodes_list, ParseException

MOCK_FREE_POOL = get_nodes_list()
_applied = dict()


SELECTOR_OP_MAP = {
    "disksize": [">", ">=", "<", "<="],
    "memory": [">", ">=", "<", "<="],
    "cpucount": [">", ">=", "<", "<="],
    "cputype": ["!=", "!~", "=~"],
    "machinetype": None,
    "name": None,
    "rack": None,
    "unit": None,
    "room": None,
    "arch": None,
}

SELECTOR_ATTR_MAP = {
    "machinetype": 'mtm',
}


class NotEnoughResourceError(Exception):
    pass


def apply_resource(count, criteria=None, instance=None):

    # Need to lock first

    if not instance:
        instance = str(uuid.uuid1())

    #free_nodes = get_free_resource()
    #if len(free_nodes) < count:
    #    raise NotEnoughResourceError("Not enough free resource.")

    # Make the selection
    selected = filter_resource(count, criteria)
    occupy_nodes(selected, g.username)

    return {instance : ','.join(selected)}


def occupy_nodes(selected, user):

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    args = ['-t', 'node', '-o', ','.join(selected), '-m', 'groups=__TFPOOL-FREE']
    cl.chdef(args)

    args = ['-t', 'node', '-o', ','.join(selected), '-p', 'groups=__TFPOOL-%s' % user]
    cl.chdef(args)


def release_nodes(selected, user):

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    args = ['-t', 'node', '-o', ','.join(selected), '-m', 'groups=__TFPOOL-%s' % user]
    cl.chdef(args)

    args = ['-t', 'node', '-o', ','.join(selected), '-p', 'groups=__TFPOOL-FREE']
    cl.chdef(args)


def _build_query_args(criteria):

    args = list()
    for key, val in criteria.items:
        if key == 'tags':
            for tag in val.split(','):
                op = '=~'
                if tag[0] == '-':
                    tag = tag[1:]
                    op = '!~'
                args.append('-w')
                args.append("usercomment%s%s" % (op, tag))

        elif key not in SELECTOR_OP_MAP:
            raise NotEnoughResourceError("Not supported criteria type: %s." % key)

        args.append('-w')
        args.append("%s==%s" % (key, val))

    return args


def filter_resource(count=1, criteria=None):

    if criteria:
        args = _build_query_args(criteria)
    else:
        args =[]

    selecting = get_free_resource(args)
    if len(selecting) < count:
        raise NotEnoughResourceError("Not enough free resource matched with the specified criteria.")

    rv = list()
    for i in range(count):
        index = random.randint(0, len(selecting)-1)
        rv.append(selecting[index])

    return rv


def free_resource(names=None):
    if names:
        selected = names.split(',')
    else:
        # TODO: get the whole occupied node by this user
        raise BadRequest("You must specify some nodes to be free.")
    occupied = get_occupied_resource(g.username)

    # the occupied would be a small list, not considering the performance
    not_owned = [item for item in selected if item not in occupied]
    if not_owned:
        raise BadRequest("Nodes are not owned by user: %s, no permission to free: %s." % (g.username, ','.join(not_owned)))

    release_nodes(selected, g.username)


def _parse_lsdef_output(output):
    nodelist = list()
    for item in output.output_msgs:
        if item.endswith("(node)"):
            nodelist.append(item.split()[0])
    return nodelist


def get_free_resource(selector=None):

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    args = ['-t', 'node', '__TFPOOL-FREE', '-s']
    if selector:
        args.extend(selector)

    try:
        result = cl.lsdef(args)

        return _parse_lsdef_output(result)
    except XCATClientError as e:
        if str(e).startswith("Could not find an object named"):
            return []
        raise


def get_occupied_resource(user):

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    args = ['-t', 'node', '__TFPOOL-%s' % user, '-s']

    try:
        result = cl.lsdef(args)

        return _parse_lsdef_output(result)
    except XCATClientError as e:
        if str(e).startswith("Could not find an object named"):
            return []
        raise
