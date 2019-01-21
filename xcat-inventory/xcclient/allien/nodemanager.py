###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from .app import dbi
from .noderange import Noderange


def get_nodes_by_range(noderange=None):

    # parse the node range in literal to a list
    nr = Noderange(noderange)

    # get attributes from nodelist
    return dbi.gettab(['nodelist'], nr.get_nodes())


def get_nodes_by_list(nodelist=None):
    return dbi.gettab(['nodelist'], nodelist)


def get_hmi_by_list(nodelist=None):
    result = {}
    for node, values in dbi.gettab(['openbmc'], nodelist).iteritems():
        result[node] = {'bmcip': values.get('openbmc.bmc'), 'username': 'root', 'password': '0penBmc'}

    return result

def get_groups(nodelist):
    unquire_groups = set()  # unique group or tag name

    # get all group names
    for node, values in nodelist.iteritems():
        groups = values.get('nodelist.groups', '')
        if groups:
            unquire_groups.update(groups.split(','))

    return list(unquire_groups)
