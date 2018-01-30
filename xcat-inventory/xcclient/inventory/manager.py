#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

from __future__ import print_function
from dbsession import DBsession
from dbfactory import dbfactory
from xcatobj import *
from exceptions import *

import os
import yaml

"""
Command-line interface to xCAT inventory import/export
"""

VALID_OBJ_TYPES = ['site', 'node', 'network', 'osimage', 'route', 'policy', 'passwd','site']
VALID_OBJ_FORMAT = ['yaml', 'json']

class InventoryFactory(object):
    __InventoryHandlers__ = {}
    __InventoryClass__ = {'node': Node, 'network': Network, 'osimage': Osimage, 'route': Route, 'policy': Policy, 'passwd': Passwd,'site': Site}
    __db__ = None
    
    def __init__(self, objtype,dbsession):
        self.objtype = objtype
        self.dbsession=dbsession

    @staticmethod
    def createHandler(objtype,dbsession):
        # non-thread-safe now
        if objtype not in InventoryFactory.__InventoryHandlers__:
            InventoryFactory.__InventoryHandlers__[objtype] = InventoryFactory(objtype,dbsession)

        return InventoryFactory.__InventoryHandlers__[objtype]

    def getDBInst(self):
        if InventoryFactory.__db__ is None:
            InventoryFactory.__db__=dbfactory(self.dbsession)

        return InventoryFactory.__db__

    def exportObjs(self, objlist, location=None):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        myclass.loadschema()
        tabs=myclass.gettablist()
        obj_attr_dict = self.getDBInst().gettab(tabs, objlist)
        objdict={}
        objdict[self.objtype]={}
        for key, attrs in obj_attr_dict.items():
            newobj = myclass.createfromdb(key, attrs)
            objdict[self.objtype].update(newobj.getobjdict())
        return objdict
        

    def importObjs(self, objlist, obj_attr_dict):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        dbdict = {}
        for key, attrs in obj_attr_dict.items():
            if not objlist or key in objlist:
                newobj = myclass.createfromfile(key, attrs)
                dbdict.update(newobj.getdbdata())
        self.getDBInst().settab(dbdict)


def dump2yaml(xcatobj, location=None):
    if not location:
        print(yaml.dump(xcatobj, default_flow_style=False))

    #TODO: store in file or directory

def dump2json(xcatobj, location=None):
    if not location:
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')))

    #TODO: store in file or directory

def validate_args(args, action):

    if args.type and args.type.lower() not in VALID_OBJ_TYPES:
        raise CommandException("Error: Invalid object type: %(t)s", t=args.type)

    if args.name and not args.type:
        raise CommandException("Error: Missing object type for object: %(o)s", o=args.name)

    if action == 'import': #extra validation for export
        if args.path and not os.path.exists(args.path):
            raise CommandException("Error: The specified path does not exist: %(p)s", p=args.path)

    if action == 'export': #extra validation for export
        if args.format and args.format.lower() not in VALID_OBJ_FORMAT:
            raise CommandException("Error: Invalid exporting format: %(f)s", f=args.format)

def export_by_type(objtype, names, location, fmt):
    dbsession=DBsession()
    hdl = InventoryFactory.createHandler(objtype,dbsession)
    objlist = []
    if names:
        objlist.extend(names.split(','))

    typedict=hdl.exportObjs(objlist, location)
    nonexistobjlist=list(set(objlist).difference(set(typedict[objtype].keys())))
    if nonexistobjlist:
        raise ObjNonExistException("Error: cannot find objects: %(f)s!", f=','.join(nonexistobjlist))
    if not fmt or fmt.lower() == 'json':
        dump2json(typedict)
    else:
        dump2yaml(typedict)
    dbsession.close() 


def export_all(location, fmt):
    dbsession=DBsession()
    #for objtype in ['node']:#VALID_OBJ_TYPES:
    wholedict={}
    for objtype in VALID_OBJ_TYPES:#VALID_OBJ_TYPES:
        hdl = InventoryFactory.createHandler(objtype,dbsession)
        wholedict.update(hdl.exportObjs([]))
    if not fmt or fmt.lower() == 'json':
        dump2json(wholedict)
    else:
        dump2yaml(wholedict)
    dbsession.close() 

def import_by_type(objtype, names, location,dryrun=None):
    dbsession=DBsession()
    hdl = InventoryFactory.createHandler(objtype,dbsession)
    objlist = []
    if names:
        objlist.extend(names.split(','))
    
    with open(location) as file:
        contents=file.read()
    try:
        obj_attr_dict = json.loads(contents)
    except ValueError:
        try: 
            obj_attr_dict = yaml.load(contents)
        except Exception,e:
            raise InvalidFileException("Error: failed to load file "+location+": "+str(e))
    if objtype: 
        if objtype not in obj_attr_dict.keys():
            raise ObjNonExistException("Error: cannot find object type '"+objtype+"' in the file "+location)
        else:
            nonexistobjlist=list(set(objlist).difference(set(obj_attr_dict[objtype].keys())))
            if nonexistobjlist:
                raise ObjNonExistException("Error: cannot find objects: %(f)s!", f=','.join(nonexistobjlist))
            else:
                hdl.importObjs(objlist, obj_attr_dict[objtype])
    else:
        hdl.importObjs(objlist, obj_attr_dict) 
    if not dryrun:
        dbsession.commit()    
    else:
        print("Dry run mode, nothing will be written to database!")
    dbsession.close()

def import_all(location,dryrun=None):
    dbsession=DBsession()
    with open(location) as file:
        contents=file.read()
    try:
        obj_attr_dict = json.loads(contents)
    except ValueError:
        try:
            obj_attr_dict = yaml.load(contents)
        except Exception,e:
            raise InvalidFileException("Error: failed to load file "+location+": "+str(e))
    
    for objtype in obj_attr_dict.keys():#VALID_OBJ_TYPES:
        hdl = InventoryFactory.createHandler(objtype,dbsession)
        hdl.importObjs([], obj_attr_dict[objtype])
    
    if not dryrun:
        dbsession.commit()
    else:
        print("Dry run mode, nothing will be written to database!")
    dbsession.close()

