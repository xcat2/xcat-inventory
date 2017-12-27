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
    __InventoryClass__ = {'node': Node, 'network': Network, 'osimage': Osimage}
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
        #tabs = myclass.getTables()
        #tabs = ['nodetype', 'switch', 'hosts', 'mac', 'noderes', 'postscripts', 'bootparams']
        myclass.loadschema()
        tabs=myclass.gettablist()
        obj_attr_dict = self.getDBInst().gettab(tabs, objlist)
        for key, attrs in obj_attr_dict.items():
            newobj = myclass.createfromdb(key, attrs)
            if not fmt or fmt.lower() == 'json':
                self.dump2json(newobj.getobjdict())
            else:
                self.dump2yaml(newobj.getobjdict())

    def importObjs(self, objlist, location):
        with open(location) as file:
            contents=file.read()
        try:
            obj_attr_dict = json.loads(contents)
        except ValueError:
            obj_attr_dict = yaml.load(contents)


        import pdb
        #pdb.set_trace()
        myclass = InventoryFactory.__InventoryClass__[self.objtype]


        dbdict = {}
        for key, attrs in obj_attr_dict.items():
            if not objlist or key in objlist:
                newobj = myclass.createfromfile(key, attrs)
                dbdict.update(newobj.getdbdata())
        self.getDBInst().settab(dbdict)

    def dump2yaml(self, xcatobj, location=None):
        if not location:
            print(yaml.dump(xcatobj, default_flow_style=False))

        #TODO: store in file or directory

    def dump2json(self, xcatobj, location=None):
        if not location:
            print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')))

        #TODO: store in file or directory

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

