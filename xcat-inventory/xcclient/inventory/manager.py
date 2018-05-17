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
import shutil

"""
Command-line interface to xCAT inventory import/export
"""

#VALID_OBJ_TYPES = ['site', 'node', 'network', 'osimage', 'route', 'policy', 'passwd','site']
VALID_OBJ_FORMAT = ['yaml', 'json']

class InventoryFactory(object):
    __InventoryHandlers__ = {}
    __InventoryClass__ = {'node': Node, 'network': Network, 'osimage': Osimage, 'route': Route, 'policy': Policy, 'passwd': Passwd,'site': Site,'zone':Zone}
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
        validversions=InventoryFactory.getAvailableSchemaVersions()
        if schemaversion not in validversions:
            raise BadSchemaException("Error: invalid schema version \""+schemaversion+"\", the valid schema versions: "+','.join(validversions)) 
        schemapath=os.path.join(os.path.dirname(__file__), 'schema/'+schemaversion+'/'+objtype+'.yaml')
        if not os.path.exists(schemapath):
            raise BadSchemaException("Error: schema file \""+schemapath+"\" does not exist, please confirm the schema version!")
        # non-thread-safe now
        if objtype not in InventoryFactory.__InventoryHandlers__:
            InventoryFactory.__InventoryHandlers__[objtype] = InventoryFactory(objtype,dbsession,schemapath)
        return InventoryFactory.__InventoryHandlers__[objtype]

    @staticmethod
    def getAvailableSchemaVersions():
        schemaversions=[]
        schemapath=os.path.join(os.path.dirname(__file__), 'schema')
        for item in os.listdir(schemapath):  
            filepath = os.path.join(schemapath, item)  
            if os.path.isdir(filepath):  
                schemaversions.append(item)
        return schemaversions
 
    @staticmethod
    def getLatestSchemaVersion():
        schemapath=os.path.join(os.path.dirname(__file__), 'schema/latest')
        realpath=os.path.realpath(schemapath)
        return os.path.basename(realpath)
   
    def getDBInst(self):
        if InventoryFactory.__db__ is None:
            InventoryFactory.__db__=dbfactory(self.dbsession)
        return InventoryFactory.__db__

    def exportObjs(self, objlist, location=None,fmt='json'):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        myclass.loadschema(self.schemapath)
        tabs=myclass.gettablist()
        obj_attr_dict = self.getDBInst().gettab(tabs, objlist)
        objdict={}
        myobjdict2dump={}
        objdict[self.objtype]={}
        for key, attrs in obj_attr_dict.items():
            if not key:
               continue
            newobj = myclass.createfromdb(key, attrs)
            myobjdict=newobj.getobjdict()
            myobjdict2dump[self.objtype]=myobjdict
            objdict[self.objtype].update(myobjdict)
            osimagefiles=newobj.getfilestosave()
            if location: 
                mydir=location+'/'+key
                if os.path.exists(mydir):
                    shutil.rmtree(mydir)
                os.mkdir(mydir) 
                myfile=mydir+'/'+'definition.yaml'
                if fmt=='yaml':
                    myfile=mydir+'/'+'definition.yaml'
                elif fmt=='json':
                    myfile=mydir+'/'+'definition.json'
                dumpobj(myobjdict2dump,fmt,myfile) 
                for imgfile in osimagefiles:
                    if os.path.exists(imgfile):
                        dstfile=mydir+imgfile
                        try:
                            os.makedirs(os.path.dirname(dstfile))
                        except OSError, e:
                            if e.errno != os.errno.EEXIST:
                                raise
                            pass
                        shutil.copyfile(imgfile,dstfile)
                    else:
                        print("The file \""+imgfile+"\" of "+self.objtype+" object \""+key+"\" does not exist",file=sys.stderr) 
        return objdict
        
    @classmethod
    def validateObjLayout(cls,obj_attr_dict):
        filekeys=set(obj_attr_dict.keys())
        schemakeys=set(cls.getvalidobjtypes())
        schemakeys.add('schema_version')
        invalidkeys=list(filekeys-schemakeys)
        if invalidkeys:
            raise InvalidFileException("Error: invalid keys found \""+' '.join(invalidkeys)+"\"!")
        
        
    def importObjs(self, objlist, obj_attr_dict,update=True):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        myclass.loadschema(self.schemapath)
        dbdict = {}
        objfiles={}
        for key, attrs in obj_attr_dict.items():
            if not objlist or key in objlist:
                newobj = myclass.createfromfile(key, attrs)
                objfiles[key]=newobj.getfilestosave()
                dbdict.update(newobj.getdbdata())
        tabs=myclass.gettablist()
        if not update:
            self.getDBInst().cleartab(tabs)
        self.getDBInst().settab(dbdict)
        return objfiles


def dumpobj(objdict, fmt='json',location=None):
    if not fmt or fmt.lower() == 'json':
        dump2json(objdict,location)
    else:
        dump2yaml(objdict,location)

def dump2yaml(xcatobj, location=None):
    if not location:
        print(yaml.dump(xcatobj, default_flow_style=False))
    else:
        f=open(location,'w')
        print(yaml.dump(xcatobj, default_flow_style=False),file=f)

    #TODO: store in file or directory

def dump2json(xcatobj, location=None):
    if not location:
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        f=open(location,'w')
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')),file=f)

    #TODO: store in file or directory

def validate_args(args, action):
    if args.type is not None:
        objtypelist=[]
        objtypelist.extend(args.type.split(','))
        invalidobjtypes=list(set(objtypelist).difference(set(InventoryFactory.getvalidobjtypes())))
        if invalidobjtypes:
            raise CommandException("Error: Invalid object type: \"%(t)s\"", t=','.join(invalidobjtypes))
        if len(objtypelist)!=1 and args.name:
            raise CommandException("Error: object names cannot be specified with multiple object types!")
    if args.name == '':
        raise CommandException("Error: Invalid object names: \"%(o)s\"", o=args.name)
    if args.name and not args.type:
        raise CommandException("Error: Missing object type for object: %(o)s", o=args.name)

    
    if action == 'import': #extra validation for export
        if not args.path:
           raise CommandException("Error: Invalid file to import: \"%(p)s\"", p=args.path)
        if not os.path.exists(args.path):
            raise CommandException("Error: The specified path does not exist: %(p)s", p=args.path)

    if action == 'export': #extra validation for export
        #if args.path and (not args.type or args.type !='osimage'):
        #    raise CommandException("Error: -f|--path is only valid for -t|--type=osimage")
        if args.format and args.format.lower() not in VALID_OBJ_FORMAT:
            raise CommandException("Error: Invalid exporting format: %(f)s", f=args.format)
        if args.exclude:
            for et in args.exclude.split(','):
                if et.lower() not in InventoryFactory.getvalidobjtypes():
                    raise CommandException("Error: Invalid object type to exclude: \"%(t)s\"", t=et)

def export_by_type(objtype, names, location=None, fmt='json',version=None,exclude=None):
    if location:
        if not objtype and not os.path.isdir(location):
            raise CommandException("Error: non-exist directory %(f)s",f=location)
        elif objtype and objtype!='osimage' and os.path.exists(location) and not os.path.isfile(location):
            raise CommandException("Error: the specified path %(f)s already exists and is not a file!", f=location)
    
    if objtype and objtype != 'osimage' and location and os.path.isdir(location):
        raise CommandException("Error: directory %(f)s specified by -f|--path is only supported when [-t|--type osimage] or export all without [-t|--type] specified",f=location)

    InventoryFactory.getLatestSchemaVersion()
    dbsession=DBsession()

    objlist = []
    objtypelist=[]
    exportall=0
    if objtype:
        objtypelist.extend(objtype.split(','))
    else:
        objtypelist.extend(InventoryFactory.getvalidobjtypes())
        exportall=1
        

    if names:
        objlist.extend(names.split(','))
    wholedict={} 

    for myobjtype in objtypelist:
        if exclude and myobjtype in exclude:
            continue
        hdl = InventoryFactory.createHandler(myobjtype,dbsession,version)
        if myobjtype == 'osimage' and location and os.path.isdir(location):
            if exportall:
                mylocation=location+'/'+myobjtype
                if not os.path.exists(mylocation):
                    os.mkdir(mylocation)
            else:
                mylocation=location
        else:
            mylocation=None
        
        typedict=hdl.exportObjs(objlist,mylocation,fmt)
        nonexistobjlist=list(set(objlist).difference(set(typedict[myobjtype].keys())))
        if nonexistobjlist:
            raise ObjNonExistException("Error: cannot find "+myobjtype+" objects: %(f)s!", f=','.join(nonexistobjlist))
        if not location or os.path.isfile(location) or myobjtype!='osimage' :
            wholedict.update(typedict)
      
    if version is None or version in ('latest'):
        version=InventoryFactory.getLatestSchemaVersion()
    wholedict['schema_version']=version    
   
    if 'osimage' in objtypelist and exportall!=1 and location and os.path.isdir(location):
        objtypelist.remove('osimage')

    if objtypelist:
        if location:
            if exportall==1 and os.path.isdir(location):
                if not fmt or fmt.lower() == 'json':
                    mylocation=location+'/cluster.json'
                else:
                    mylocation=location+'/cluster.yaml'
                dumpobj(wholedict, fmt,mylocation)
            else:
                dumpobj(wholedict, fmt,location)
        else: 
            if not fmt or fmt.lower() == 'json':
                dump2json(wholedict)
            else:
                dump2yaml(wholedict)
    dbsession.close() 



def importfromfile(objtypelist, objlist, location,dryrun=None,version=None,update=True):
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
    objfiledict={}
    if objtypelist: 
        nonexistobjtypelist=list(set(objtypelist).difference(set(obj_attr_dict.keys())))
        if nonexistobjtypelist:
            raise ObjNonExistException("Error: cannot find object types: %(f)s in the file "+location+'!', f=','.join(nonexistobjtypelist))
        for myobjtype in objtypelist:
            nonexistobjlist=list(set(objlist).difference(set(obj_attr_dict[myobjtype].keys())))
            if nonexistobjlist:
                raise ObjNonExistException("Error: cannot find objects: %(f)s!", f=','.join(nonexistobjlist))
            hdl = InventoryFactory.createHandler(myobjtype,dbsession,version)
            if myobjtype not in objfiledict.keys():
                objfiledict[myobjtype]={}
            objfiledict[myobjtype].update(hdl.importObjs(objlist, obj_attr_dict[myobjtype],update))
    else:
        for objtype in obj_attr_dict.keys():#VALID_OBJ_TYPES:
            hdl = InventoryFactory.createHandler(objtype,dbsession,version)
            if objtype not in objfiledict.keys():
                objfiledict[objtype]={}
            objfiledict[objtype].update(hdl.importObjs([], obj_attr_dict[objtype],update))

    if not dryrun:
        try:
            dbsession.commit()   
        except Exception, e: 
            raise DBException("Error on commit DB transactions: "+str(e))
        else:
            print('Inventory import successfully!')
    else:
        print("Dry run mode, nothing will be written to database!")
    dbsession.close()
    return objfiledict


def importobjdir(location,dryrun=None,version=None,update=True):
    objfile=None
    if os.path.exists(location+'/'+'definition.yaml'):
        objfile=location+'/'+'definition.yaml'
    elif os.path.exists(location+'/'+'definition.json'):
        objfile=location+'/'+'definition.json'    
    else:
        raise InvalidFileException("Error: no definition.json or definition.yaml found under \""+location+"\""+"!")
    objfilesdict=importfromfile(None,None,objfile,dryrun,version,update)
    if len(objfilesdict.keys()) !=1:
        raise InvalidFileException("Error: invalid definition file: \""+objfile+"\": should contain only 1 object type")  
    else:
        objtype=objfilesdict.keys()[0]
    if len(objfilesdict[objtype].keys()) !=1:
        raise InvalidFileException("Error: invalid definition file: \""+objfile+"\": should contain only 1 object")
    else:
        objname=objfilesdict[objtype].keys()[0]
    objfiles=objfilesdict[objtype][objname]
    for myfile in objfiles:
        srcfile=location+myfile
        if os.path.exists(srcfile):
            try:
                os.makedirs(os.path.dirname(myfile))
            except OSError, e:
                if e.errno != os.errno.EEXIST:
                    raise
                pass
            shutil.copyfile(srcfile,myfile)
        else:
            print("the file \""+srcfile+"\" of osimage \""+objname+"\" does not exist!",file=sys.stderr)

def importfromdir(location,objtype='osimage',objnames=None,dryrun=None,version=None,update=True):
    objnamelist=[]
    if not objnames:
        objnamelist=os.listdir(location)
    else:
        objnamelist=objnames.split(',')
    for objname in objnamelist:
        if os.path.exists(location+'/'+objname):
            objdir=location+'/'+objname
            importobjdir(objdir,dryrun,version,update)
        else:
            print("the specified object \""+objname+"\" does not exist under \""+location+"\"!",file=sys.stderr)
     
def importobj(location,objtype,objnames=None,dryrun=None,version=None,update=True):
     objtypelist=[]
     if objtype:
         objtypelist=objtype.split(',')

     objnamelist=[]
     if objnames:
         objnamelist=objnames.split(',')

     if os.path.isfile(location):
         importfromfile(objtypelist, objnamelist, location,dryrun,version,update)
     elif os.path.isdir(location):
         clusterfile=None
         if os.path.exists(location+'/'+'cluster.yaml'):
             clusterfile=location+'/'+'cluster.yaml'
         elif os.path.exists(location+'/'+'cluster.json'):
             clusterfile=location+'/'+'cluster.json'

         #this is a cluster directory
         if clusterfile:
             myobjtypelist=[]
             myobjtypelist.extend(objtypelist)

             if 'osimage' in myobjtypelist:
                 myobjtypelist.remove('osimage')
                 if myobjtypelist:
                     importfromfile(myobjtypelist,objnamelist,clusterfile,dryrun,version,update)
                 importfromdir(location+'/osimage/','osimage',objnames,dryrun,version,update)
             else:
                 importfromfile(objtypelist,objnamelist,clusterfile,dryrun,version,update)
         else:
             objfile=None
             if os.path.exists(location+'/'+'definition.yaml'):
                 objfile=location+'/'+'definition.yaml'
             elif os.path.exists(location+'/'+'definition.json'):
                 objfile=location+'/'+'definition.json'

             #this is a osimage derectory
             if 'osimage' in objtypelist:
                 if objfile:
                     importobjdir(location,'osimage',objnames,dryrun,version,update)
                 else:
                     importfromdir(location,'osimage',objnames,dryrun,version,update)
             else:
                 raise InvalidFileException("Error: invalid directory "+location+"!")
                 
     else:
         raise InvalidFileException("Error: invalid path \""+location+"\""+"!")

