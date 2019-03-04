###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask import g

from .app import dbi, dbsession
from .noderange import NodeRange
from ..inventory.manager import InventoryFactory

OPT_QUERY_THRESHHOLD = 18


def get_nodes_list():

    # get all records from nodelist table
    return dbi.gettab(['nodelist'])

def get_nodes_by_range(noderange=None):

    # parse the node range in literal to a list objects (might be node, group, or non existence)
    nr = NodeRange(noderange)

    # Get attributes from nodelist
    if nr.all or nr.size > OPT_QUERY_THRESHHOLD:
        # query whole if the range size larger than 255
        dataset = dbi.gettab(['nodelist', 'nodegroup'])
    else:
        dataset = dbi.gettab(['nodelist', 'nodegroup'], nr.nodes)

    g.nodeset = dataset
    if nr.all:
        return dataset.keys(), None

    nodelist = dict()
    nonexistence = list()
    for name in nr.nodes:
        if name in dataset:
            nodelist[name] = dataset[name]
        else:
            nonexistence.append(name)

    # For nonexistence, need to check if it is a group or tag
    return nodelist.keys(), nonexistence


def _check_groups_in_noderange(nodelist, noderange):
    unique_groups = set()  # unique group or tag name

    # get all group names
    for node, values in nodelist.iteritems():
        groups = values.get('nodelist.groups', '')
        if groups:
            unique_groups.update(groups.split(','))

    return list(unique_groups)


def get_nodes_by_list(nodelist=None):
    return dbi.gettab(['nodelist'], nodelist)


def get_hmi_by_list(nodelist=None):
    result = {}
    for node, values in dbi.gettab(['openbmc'], nodelist).iteritems():
        result[node] = {'bmcip': values.get('openbmc.bmc'), 'username': 'root', 'password': '0penBmc'}

    return result


def get_node_attributes():
    pass


def get_inventory_by_type(objtype, ids=None):
    hdl = InventoryFactory.createHandler(objtype, dbsession, None)


    wants = None
    if ids:
        if type(ids) == 'list':
            wants = ids
        else:
            wants = [ids]

    result = hdl.exportObjs(wants, None, fmt='json')
    if not result:
        return []

    return result[objtype]