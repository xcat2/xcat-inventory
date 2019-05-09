###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import g, current_app

from xcclient.xcatd import XCATClient, XCATClientParams

from .app import dbi, dbsession, cache
from .noderange import NodeRange
from ..inventory.manager import InventoryFactory
from ..inventory.exceptions import *

OPT_QUERY_THRESHHOLD = 18


def get_nodes_list(ids=None):

    wants = []
    if ids:
        if type(ids) is list:
            wants.extend(ids)
        else:
            wants.append(ids)

    try:
        nodes = cache.get('nodes_list_all')
    except:
        # Error when connection cache
        nodes = None

    if nodes is None:
        # get wanted records from nodelist table
        nodes = dbi.gettab(['nodelist'], wants)
        if not wants:
            try:
                cache.set('nodes_list_all', nodes, timeout=60)
            except:
                pass

    if wants:

        results = dict()
        for key in wants:
            if key in nodes:
                results[key] = nodes.get(key)
    else:
        results = dict(nodes)

    return results


@cache.cached(timeout=50, key_prefix='get_node_basic')
def get_node_basic(id):

    return dbi.gettab(['nodelist'], [id])


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


@cache.memoize(timeout=50)
def get_node_attributes(node):

    target_node = get_nodes_list(node)
    if not target_node:
        return None

    groups = target_node.values()[0].get('nodelist.groups')

    # combine the attribute from groups
    needs = [node]
    needs.extend(groups.split(','))
    return get_node_inventory('node', needs)


def get_node_inventory(objtype, ids=None):
    hdl = InventoryFactory.createHandler('node', dbsession, None)


    wants = None
    if ids:
        if type(ids) is list:
            wants = ids
        else:
            wants = [ids]

    result = hdl.exportObjs(wants, None, fmt='json')
    if not result:
        return []

    # TODO: filter by objtype
    return result['node']


def get_inventory_by_type(objtype, ids=None):
    hdl = InventoryFactory.createHandler(objtype, dbsession, None)

    wants = None
    if ids:
        if type(ids) is list:
            wants = ids
        else:
            wants = [ids]

    return hdl.exportObjs(wants, None, fmt='json').get(objtype)

def upd_inventory_by_type(objtype, obj_attr_dict, clean=False):
    hdl = InventoryFactory.createHandler(objtype, dbsession, None)

    hdl.importObjs(obj_attr_dict.keys(), obj_attr_dict, update=not clean, envar={})
    dbsession.commit()

def del_table_entry_by_key(objtype, obj_attr_dict):
    hdl = InventoryFactory.createHandler(objtype, dbsession, None)

    hdl.deleteTabEntrybykey(objtype, obj_attr_dict)
    dbsession.commit()

def add_table_entry_by_key(objtype, obj_attr_dict):
    hdl = InventoryFactory.createHandler(objtype, dbsession, None) 
    hdl.addTabEntrybykey(objtype, obj_attr_dict)
    dbsession.commit()

def del_inventory_by_type(objtype, obj_list):
    """delete objects from data store"""
    # hdl = InventoryFactory.createHandler(objtype, dbsession, None)

    #return hdl.importObjs(obj_list, {}, update=False, envar={})

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    result = cl.rmdef(args=['-t', objtype, '-o', ','.join(obj_list)])
    return result.output_msgs


def patch_inventory_by_type(objtype, obj_name, obj_d):
    """modify object attribute"""
    if not obj_d:
        raise InvalidValueException("Input data should not be None.")
    if not type(obj_d) in [dict, list]:
        raise InvalidValueException("Input data format should be dict or list.")
    if not obj_d.keys()[0] == "modify":
        raise InvalidValueException("Input data key should be modify.")
    if not obj_d.get('modify'):
        raise InvalidValueException("Input data value should be null.")
    kv_pair=''
    for key,value in obj_d.get('modify').items():
        if kv_pair is None:
            kv_pair=key+"="+value
        else:
            kv_pair=kv_pair+" "+key+"="+value
    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    result = cl.chdef(args=['-t', objtype, '-o', obj_name, kv_pair])
    
    return dict(outputs=result.output_msgs)


def transform_from_inv(obj_d):
    """transform the inventory object model(dict for collection) to a list"""
    assert obj_d is not None
    assert type(obj_d) is dict

    results = list()
    while len(obj_d) > 0:
        name, spec = obj_d.popitem()
        rd = dict(meta=dict(name=name), spec=spec)
        results.append(rd)

    return results


def validate_resource_input_data(obj_d, obj_name=None):
    """input object data should have meta and spec"""
    if not obj_d:
        raise InvalidValueException("Input data should not be None.")
    if not type(obj_d) in [dict, list]:
        raise InvalidValueException("Input data format should be dict or list.")
    if not len(obj_d.keys())==2:
        raise InvalidValueException("Input data keys number is wrong.")
    if not obj_d.keys()[0]=="meta":
        raise InvalidValueException("Input data first key "+obj_d.keys()[0]+" should be meta.")
    if not obj_d.keys()[1]=="spec":
        raise InvalidValueException("Input data second key "+obj_d.keys()[1]+" is spec.")
    if not type(obj_d['spec']) in [dict]:
        raise InvalidValueException("spec type shoule be dict.")
    if not type(obj_d['meta']) in [dict]:
        raise InvalidValueException("meta type shoule be dict.")
    if not len(obj_d['meta'])==1:
        raise InvalidValueException("meta key number should be 1.")
    if not obj_d['meta'].keys()[0]=="name":
        raise InvalidValueException("meta key should be name.")
    if not obj_d['meta'].get('name'):
        raise InvalidValueException("meta name should not be null");
    if obj_name:
        if not obj_d['meta'].get('name')==obj_name:
            raise InvalidValueException("meta name "+obj_d['meta'].get('name')+" is not the same with resource name "+obj_name+".")


def transform_to_inv(obj_d):
    """transform the REST object(list or dict) to inventory object model(dict for collection)"""
    assert obj_d is not None
    assert type(obj_d) in [dict, list]

    def _dict_to_inv(src):
        assert 'meta' in src
        name = obj_d['meta'].get('name')
        # TODO: name = name or random_name()
        val = obj_d.get('spec')
        return name, val

    result = dict()
    if type(obj_d) is dict:
        n, v = _dict_to_inv(obj_d)
        result[n] = v
    else:
        # Then it could be a list
        for ob in obj_d:
            n, v = _dict_to_inv(ob)
            result[n] = v
    return result


def split_inventory_types(types):

    include = list()
    exclude = ['credential']

    # get the include and exclude
    for rt in types:
        rt = rt.strip()
        if not rt:
            raise InvalidValueException("Invalid inventory type name: (%s)" % rt)

        if rt.startswith('-'):
            ert = rt[1:]
            if ert not in InventoryFactory.getvalidobjtypes():
                raise InvalidValueException("Invalid inventory type name: (%s)" % rt)
            exclude.append(ert)
        else:
            if rt not in InventoryFactory.getvalidobjtypes():
                raise InvalidValueException("Invalid inventory type name: (%s)" % rt)
            include.append(rt)

    return include, exclude
