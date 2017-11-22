#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

import dbsession
from xcatobj import *

import os

"""
Command-line interface to xCAT inventory import/export
"""

def validate_args(args, action):
    #print(args)
    pass

def check_inventory_type(objtype, name):
    pass

def export_by_type(objtype, name, location, fmt):
    print("export type of %s inventory to %s in %s format" % (objtype, location, fmt))
    if name:
        print("specified dedicate object: %s" % name)

def export_all(location, fmt):
    session = dbsession.loadSession()
    nodelist = ['c910f03c17k41','c910f03c17k42']
    nodelist_value = query_nodelist_by_key(session, nodelist)

    Node.loaddb(nodelist_value)
    Node.loadschema(os.path.join(os.path.dirname(__file__), node.yaml))
    for node in Node.listobj():
        if fmt in ['yaml', 'YAML']:
            Node(node).dump2yaml()
        else:
            Node(node).dump2json()

def import_by_type(objtype, name, location):
    print("import type of %s inventory from %s" % (objtype, location))
    if name:
        print("specified dedicate object: %s" % name)

def import_all(location):
    print("import inventory from %s" % location)
