#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

import dbsession
from xcatobj import *
from xcclient.shell import CommandException

import os

"""
Command-line interface to xCAT inventory import/export
"""

VALID_OBJ_TYPES = ['site', 'node', 'network', 'osimage']
VALID_OBJ_FORMAT = ['yaml', 'json']

def validate_args(args, action):

    if args.type and args.type.lower() not in VALID_OBJ_TYPES:
        raise CommandException("Invalid object type: %(t)s", t=args.type)

	if args.name and not args.type:
		raise CommandException("Missing object type for object: %(o)s", o=args.name)

    if action == 'import': #extra validation for export
        if args.path and not os.path.exists(args.path):
            raise CommandException("The specified path does not exist: %(p)s", p=args.path)

    if action == 'export': #extra validation for export
        if args.format and args.format.lower() not in VALID_OBJ_FORMAT:
            raise CommandException("Invalid exporting format: %(f)s", f=args.format)

def export_by_type(objtype, name, location, fmt):
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
