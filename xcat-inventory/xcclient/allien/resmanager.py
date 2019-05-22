###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
import random
import re
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


def apply_resource(count, criteria=None, instance=None):

    # Need to lock first

    if not instance:
        instance = str(uuid.uuid1())

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
    tags = None
    for key, val in criteria.items():
        if key == 'tags':
            tags = val
        elif key not in SELECTOR_OP_MAP:
            current_app.logger.warn("Not supported criteria type: %s." % key)
            # not report error at this time, but if user specify wrong attribute, it will cause unexcepted 500 error
            # raise BadRequest("Not supported criteria type: %s." % key)

        args.append('-w')
        args.append("%s==%s" % (SELECTOR_ATTR_MAP.get(key, key), val))

    return args, tags


def _parse_node_tags(tagstr):

    if not tagstr:
        return

    matched = re.search(r"tags=\[(.*)\]", tagstr)

    if not matched:
        return

    return matched.groups()[0].split(',')


def _parse_rule_dict(rulestr):
    """parse rule string for tag to a dict with tag -> rule

    Args:
        rulestr: comma separated rule string (a,b,-c,-d)

    Returns:
        A dict mapping tags to the corresponding rule.
        For example:

            {
             'tag1':True,
             'tag2':False
            }

    Note: if a tag in both allow and forbid rule, then it last order will take effective
    """
    rv = dict()

    rulestr = rulestr.strip()
    if not rulestr:
        return rv
    rules = rulestr.split(',')

    for rule in rules:
        if rule.startswith('-'):
            rule = rule[1:]
            rv[rule] = False
        else:
            rv[rule] = True
    return rv


def _match_with_tags(tags, rules):
    """Determine if the node tags matching with the rule

    Args:
        tags:  comma separated rule string (a,b,-c,-d)
        rules: rule dict

    Returns:
        True or False

    """
    for rule in rules.keys():
        rr = rules[rule]
        # not to have the tag rule
        if not rr and rule in tags:
            return False

        # must have the tag rule
        elif rr not in tags:
            return False

    return True


def _filter_with_tag(nodelist, count, rule):

    pool = get_nodes_list(nodelist)

    selected = list()
    rules = _parse_rule_dict(rule)
    for i in range(count):
        node = random.sample(pool.keys(), 1)[0]
        tags = _parse_node_tags(pool[node]['comments'])

        # Select the node when no rules or pass the rules
        if not len(rules) or _match_with_tags(tags, rules):
            selected.append(node)
        del pool[node]

    return selected


def filter_resource(count=1, criteria=None):

    if criteria:
        args, tags = _build_query_args(criteria)
    else:
        args = []
        tags = ''

    selecting = get_free_resource(args)
    if len(selecting) < count:
        raise BadRequest("Not enough free resource matched with the specified attributes.")

    tags = tags or ''
    selected = _filter_with_tag(selecting, count, tags)
    if len(selected) < count:
        raise BadRequest("Not enough free resource matched with the specified tags.")

    return selected


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
        for line in item.split('\n'):
            if line.endswith("(node)"):
                nodelist.append(line.split()[0])
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
