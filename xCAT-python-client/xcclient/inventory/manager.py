#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

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
    print("export inventory to %s in %s format" % (location, fmt))

def import_by_type(objtype, name, location):
    print("import type of %s inventory from %s" % (objtype, location))
    if name:
        print("specified dedicate object: %s" % name)

def import_all(location):
    print("import inventory from %s" % location)