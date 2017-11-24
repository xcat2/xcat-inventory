#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

from __future__ import print_function

from dbfactory import dbfactory
from xcatobj import *
from xcclient.shell import CommandException

import os
import yaml

"""
Command-line interface to xCAT inventory import/export
"""

VALID_OBJ_TYPES = ['site', 'node', 'network', 'osimage']
VALID_OBJ_FORMAT = ['yaml', 'json']

class InventoryFactory(object):
    __InventoryHandlers__ = {}
    __InventoryClass__ = {'node': Node}
    __db__ = None

    def __init__(self, objtype):
        self.objtype = objtype

    @staticmethod
    def createHandler(objtype):
        # non-thread-safe now
        if objtype not in InventoryFactory.__InventoryHandlers__:
            InventoryFactory.__InventoryHandlers__[objtype] = InventoryFactory(objtype)

        return InventoryFactory.__InventoryHandlers__[objtype]

    def getDBInst(self):
        if InventoryFactory.__db__ is None:
            InventoryFactory.__db__=dbfactory()

        return InventoryFactory.__db__

    def exportObjs(self, objlist, fmt, location):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        #myclass.loadschema()
        myclass.loadschema(os.path.join(os.path.dirname(__file__), 'node.yaml'))
        #tabs = myclass.getTables()
        tabs = ['nodetype', 'switch', 'hosts', 'mac', 'noderes', 'postscripts', 'bootparams']
        obj_attr_dict = self.getDBInst().gettab(tabs, objlist)
        for key, attrs in obj_attr_dict.items():
            newobj = myclass.createfromdb(key, attrs)
            if not fmt or fmt.lower() == 'json':
                self.dump2json(newobj.getobjdict())
            else:
                self.dump2yaml(newobj.getobjdict())

    def exportObj(self):
        pass

    def importObjs(self,objlist,location):
        with open(location) as json_data:
            d = json.load(json_data)
            print(d)
        return
        myclass = __InventoryClass__[self.objtype]
        #myclass.loadschema()
        myclass.loadschema(os.path.join(os.path.dirname(__file__), 'node.yaml'))

        self.getDBInst.gettab(tabs, objlist)
        for key, attrs in obj_attr_dict.items():
            newobj = myclass.createfromfile(key, attrs)
            if fmt.lower() == 'json':
                self.dump2json(newobj.setDict())
            else:
                self.dump2yaml(newobj.setDict())

    def importObj(self):
        pass

    def dump2yaml(self, xcatobj):
        print(yaml.dump(xcatobj, default_flow_style=False))

    def dump2json(self, xcatobj):
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')))

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

def export_by_type(objtype, names, location, fmt):
    hdl = InventoryFactory.createHandler(objtype)
    objlist = []
    if names:
        objlist.extend(names.split(','))

    hdl.exportObjs(objlist, fmt, location)

def export_all(location, fmt):
    for objtype in ['node']:#VALID_OBJ_TYPES:
        hdl = InventoryFactory.createHandler(objtype)
        hdl.exportObjs([], fmt, location)

def import_by_type(objtype, names, location):
    hdl = InventoryFactory.createHandler(objtype)
    objlist = []
    if names:
        objlist.extend(names.split(','))

    hdl.importObjs(objlist, location)

def import_all(location):
    for objtype in ['node']:#VALID_OBJ_TYPES:
        hdl = InventoryFactory.createHandler(objtype)
        hdl.importObjs([], location)
