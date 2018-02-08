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

#VALID_OBJ_TYPES = ['site', 'node', 'network', 'osimage', 'route', 'policy', 'passwd','site']
VALID_OBJ_FORMAT = ['yaml', 'json']

class InventoryFactory(object):
    __InventoryHandlers__ = {}
    __InventoryClass__ = {'node': Node, 'network': Network, 'osimage': Osimage, 'route': Route, 'policy': Policy, 'passwd': Passwd,'site': Site}
    __db__ = None
    
    def __init__(self, objtype,dbsession,schemapath):
        self.objtype = objtype
        self.dbsession=dbsession
        self.schemapath=schemapath

    @classmethod
    def getvalidobjtypes(cls):
        return cls.__InventoryClass__.keys()

    @staticmethod
    def createHandler(objtype,dbsession,schemaversion='latest'):
        if schemaversion is None:
            schemaversion='latest'
        schemapath=os.path.join(os.path.dirname(__file__), 'schema/'+schemaversion+'/'+objtype+'.yaml')
        if not os.path.exists(schemapath):
            raise BadSchemaException("Error: schema file \""+schemapath+"\" does not exist, please confirm the schema version!")
        # non-thread-safe now
        if objtype not in InventoryFactory.__InventoryHandlers__:
            InventoryFactory.__InventoryHandlers__[objtype] = InventoryFactory(objtype,dbsession,schemapath)
        return InventoryFactory.__InventoryHandlers__[objtype]

    @staticmethod
    def getLatestSchemaVersion():
        schemapath=os.path.join(os.path.dirname(__file__), 'schema/latest')
        realpath=os.path.realpath(schemapath)
        return os.path.basename(realpath)
   
    def getDBInst(self):
        if InventoryFactory.__db__ is None:
            InventoryFactory.__db__=dbfactory(self.dbsession)
        return InventoryFactory.__db__

    def exportObjs(self, objlist, location=None):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        myclass.loadschema(self.schemapath)
        tabs=myclass.gettablist()
        obj_attr_dict = self.getDBInst().gettab(tabs, objlist)
        objdict={}
        objdict[self.objtype]={}
        for key, attrs in obj_attr_dict.items():
            newobj = myclass.createfromdb(key, attrs)
            objdict[self.objtype].update(newobj.getobjdict())
        return objdict
        
    @classmethod
    def validateObjLayout(cls,obj_attr_dict):
        filekeys=set(obj_attr_dict.keys())
        schemakeys=set(cls.getvalidobjtypes())
        schemakeys.add('schema_version')
        invalidkeys=list(filekeys-schemakeys)
        if invalidkeys:
            raise InvalidFileException("Error: invalid keys found \""+' '.join(invalidkeys)+"\"!")
        
        
    def importObjs(self, objlist, obj_attr_dict):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        myclass.loadschema(self.schemapath)
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

    if args.type and args.type.lower() not in InventoryFactory.getvalidobjtypes():
        raise CommandException("Error: Invalid object type: %(t)s", t=args.type)

    if args.name and not args.type:
        raise CommandException("Error: Missing object type for object: %(o)s", o=args.name)

    if action == 'import': #extra validation for export
        if args.path and not os.path.exists(args.path):
            raise CommandException("Error: The specified path does not exist: %(p)s", p=args.path)

    if action == 'export': #extra validation for export
        if args.format and args.format.lower() not in VALID_OBJ_FORMAT:
            raise CommandException("Error: Invalid exporting format: %(f)s", f=args.format)

def export_by_type(objtype, names, location, fmt,version=None):
    InventoryFactory.getLatestSchemaVersion()
    dbsession=DBsession()
    hdl = InventoryFactory.createHandler(objtype,dbsession,version)
    objlist = []
    if names:
        objlist.extend(names.split(','))

    typedict=hdl.exportObjs(objlist, location)
    nonexistobjlist=list(set(objlist).difference(set(typedict[objtype].keys())))
    if nonexistobjlist:
        raise ObjNonExistException("Error: cannot find objects: %(f)s!", f=','.join(nonexistobjlist))
   
    if version is None or version in ('latest'):
        version=InventoryFactory.getLatestSchemaVersion()
    typedict['schema_version']=version    
    
    if not fmt or fmt.lower() == 'json':
        dump2json(typedict)
    else:
        dump2yaml(typedict)
    dbsession.close() 


def export_all(location, fmt,version=None):
    dbsession=DBsession()
    wholedict={}
    for objtype in InventoryFactory.getvalidobjtypes():
        hdl = InventoryFactory.createHandler(objtype,dbsession,version)
        wholedict.update(hdl.exportObjs([]))

    if version is None or version in ('latest'):
        version=InventoryFactory.getLatestSchemaVersion()
    wholedict['schema_version']=version

    if not fmt or fmt.lower() == 'json':
        dump2json(wholedict)
    else:
        dump2yaml(wholedict)
    dbsession.close() 

def import_by_type(objtype, names, location,dryrun=None,version=None):
    dbsession=DBsession()

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
  
    versinfile=None
    if 'schema_version' in obj_attr_dict.keys():
        versinfile=obj_attr_dict['schema_version']
        del obj_attr_dict['schema_version']
    if not versinfile or versinfile == 'latest':
        versinfile=InventoryFactory.getLatestSchemaVersion()
    if version == 'latest':
        version=InventoryFactory.getLatestSchemaVersion()
    if version and version != versinfile:
        raise CommandException("Error: the specified schema version \""+version+"\" does not match the schema_version \""+versinfile+"\" in input file "+location ) 
    version=versinfile

    hdl = InventoryFactory.createHandler(objtype,dbsession,version)

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

def import_all(location,dryrun=None,version=None):
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

    versinfile=None
    if 'schema_version' in obj_attr_dict.keys():
        versinfile=obj_attr_dict['schema_version']
        del obj_attr_dict['schema_version']
    if not versinfile or versinfile == 'latest':
        versinfile=InventoryFactory.getLatestSchemaVersion()
    if version == 'latest':
        version=InventoryFactory.getLatestSchemaVersion()
    if version and version != versinfile:
        raise CommandException("Error: the specified schema version \""+version+"\" does not match the schema_version \""+versinfile+"\" in input file "+location )
    version=versinfile
   
    InventoryFactory.validateObjLayout(obj_attr_dict) 
    for objtype in obj_attr_dict.keys():#VALID_OBJ_TYPES:
        hdl = InventoryFactory.createHandler(objtype,dbsession,version)
        hdl.importObjs([], obj_attr_dict[objtype])
    
    if not dryrun:
        dbsession.commit()
    else:
        print("Dry run mode, nothing will be written to database!")
    dbsession.close()

