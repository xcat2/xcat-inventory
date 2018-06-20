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
from utils import *

import os
import yaml
import shutil
from jinja2 import Template,Environment,meta,FileSystemLoader

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

    def exportObjs(self, objlist, location=None,fmt='json',comment=None):
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
            myobjdict2dump['schema_version']=self.getcurschemaversion()
            objdict[self.objtype].update(myobjdict)
            osimagefiles=newobj.getfilestosave()
            if location: 
                mydir=os.path.join(location,key)
                if os.path.exists(mydir):
                    shutil.rmtree(mydir)
                os.mkdir(mydir) 
                if fmt=='yaml':
                    myfile=os.path.join(mydir,'definition.yaml')
                elif fmt=='json':
                    myfile=os.path.join(mydir,'definition.json')
                dumpobj(myobjdict2dump,fmt,myfile) 
                with open(myfile, "a") as f:
                    f.write(comment)
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
                        print("Warning: The file \"%s\" of \"%s\" object \"%s\" does not exist"%(imgfile,self.objtype,key),file=sys.stderr) 
        return objdict
        
    @classmethod
    def validateObjLayout(cls,obj_attr_dict):
        filekeys=set(obj_attr_dict.keys())
        schemakeys=set(cls.getvalidobjtypes())
        schemakeys.add('schema_version')
        invalidkeys=list(filekeys-schemakeys)
        if invalidkeys:
            raise InvalidFileException("Error: invalid keys found \""+' '.join(invalidkeys)+"\"!")
        
        
    def importObjs(self, objlist, obj_attr_dict,update=True,envar=None):
        myclass = InventoryFactory.__InventoryClass__[self.objtype]
        myclass.loadschema(self.schemapath)
        dbdict = {}
        objfiles={}
        for key, attrs in obj_attr_dict.items():
            if not objlist or key in objlist:
                if self.objtype == 'osimage' and envar is not None:
                    Util_setdictval(attrs,'environvars',envar)   
                newobj = myclass.createfromfile(key, attrs)
                objfiles[key]=newobj.getfilestosave()
                dbdict.update(newobj.getdbdata())
        tabs=myclass.gettablist()
        if not update:
            self.getDBInst().cleartab(tabs)
        self.getDBInst().settab(dbdict)
        return objfiles

    def getcurschemaversion(self):
        if self.schemapath:
            return os.path.basename(os.path.dirname(os.path.realpath(self.schemapath)))
        else:
            return 'latest'

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
        objtypelist.extend([n.strip() for n in args.type.split(',')])
        invalidobjtypes=list(set(objtypelist).difference(set(InventoryFactory.getvalidobjtypes())))
        if invalidobjtypes:
            raise CommandException("Error: Invalid object type: \"%(t)s\"", t=','.join(invalidobjtypes))
        if len(objtypelist)!=1 and args.name:
            raise CommandException("Error: object names cannot be specified with multiple object types!")
    if args.name == '':
        raise CommandException("Error: Invalid object names: \"%(o)s\"", o=args.name)
    if args.name and not args.type:
        raise CommandException("Error: Missing object type for object: %(o)s", o=args.name)
    if args.path and args.directory:
        raise CommandException("Error: -f|--path and -d|--dir cannot be used together!")
    if args.directory:
        if not os.path.exists(args.directory):
            raise CommandException("Error: the specified directory %(d)s does not exist!", d=args.directory)
        if not os.path.isdir(args.directory):
            raise CommandException("Error: the specified directory %(d)s is not a directory!", d=args.directory)
    if args.path:
        if os.path.exists(args.path):
            if not os.path.isfile(args.path):
                raise CommandException("Error: the specified file %(f)s already exists, is not a file!", f=args.path)
        else:
            mydir=os.path.dirname(args.path)
            myfile=os.path.basename(args.path)
            if not myfile:
                raise CommandException("Error: %(f)s is not a file!", f=args.path)
            if not os.path.isdir(mydir):
                raise CommandException("Error: the directory %(f)s does not exist or is not a directory!", f=mydir)
       
    
    if action == 'import': #extra validation for export
        if not args.path and not args.directory:
           raise CommandException("Error: expect inventory file(-f|--path) or inventory directory(-d|--direcotry)!")
        if args.path and not os.path.exists(args.path):
            raise CommandException("Error: The specified inventory file does not exist: %(p)s", p=args.path)
        if args.directory and not os.path.exists(args.directory):
            raise CommandException("Error: The specified inventory directory does not exist: %(p)s", p=args.path)

    if action == 'export': #extra validation for export
        #if args.path and (not args.type or args.type !='osimage'):
        #    raise CommandException("Error: -f|--path is only valid for -t|--type=osimage")
        if args.format and args.format.lower() not in VALID_OBJ_FORMAT:
            raise CommandException("Error: Invalid exporting format: %(f)s", f=args.format)
        if args.exclude:
            for et in [n.strip() for n in args.exclude.split(',')]:
                if et.lower() not in InventoryFactory.getvalidobjtypes():
                    raise CommandException("Error: Invalid object type to exclude: \"%(t)s\"", t=et)

def export_by_type(objtype, names, destfile=None, destdir=None, fmt='json',version=None,exclude=None):
    if objtype and objtype != 'osimage' and destdir:
        raise CommandException("Error: directory %(f)s specified by -f|--path is only supported when [-t|--type osimage] or export all without [-t|--type] specified",f=destdir)

    if not fmt:
        fmt='json'
    InventoryFactory.getLatestSchemaVersion()
    dbsession=DBsession()
    
    xcatversion='XCAT Version'
    (retcode,out,err)=runCommand('XCATBYPASS=0 lsxcatd -v')
    if retcode==0:
        xcatversion=out

    objlist = []
    objtypelist=[]
    exportall=0
    if objtype:
        objtypelist.extend([n.strip() for n in objtype.split(',')])
    else:
        objtypelist.extend(InventoryFactory.getvalidobjtypes())
        exportall=1

    if names:
        objlist.extend([n.strip() for n in names.split(',')])

    wholedict={} 
    for myobjtype in objtypelist:
        if exclude and myobjtype in exclude:
            continue
        hdl = InventoryFactory.createHandler(myobjtype,dbsession,version)
        if myobjtype == 'osimage' and destdir:
            if exportall:
                mylocation=os.path.join(destdir,myobjtype)
                if os.path.exists(mylocation):
                    shutil.rmtree(mylocation)
                os.mkdir(mylocation)
            else:
                mylocation=destdir
        else:
            mylocation=None
        
        typedict=hdl.exportObjs(objlist,mylocation,fmt,"#%s"%(xcatversion))
        nonexistobjlist=list(set(objlist).difference(set(typedict[myobjtype].keys())))
        if nonexistobjlist:
            raise ObjNonExistException("Error: cannot find "+myobjtype+" objects: %(f)s!", f=','.join(nonexistobjlist))
        if destdir and myobjtype == 'osimage':
            print("The %s objects has been exported to directory %s"%(myobjtype,destdir))

        #do not add osimage objects to %wholedict when export inventory data to a directory
        if not destdir or myobjtype!='osimage':
            wholedict.update(typedict)
      
    if version is None or version in ('latest'):
        version=InventoryFactory.getLatestSchemaVersion()
    wholedict['schema_version']=version    
   
    if 'osimage' in objtypelist and destdir:
        objtypelist.remove('osimage')

    if objtypelist:
        if destdir and exportall==1:
            if not fmt or fmt.lower() == 'json':
                mylocation=os.path.join(destdir,'cluster.json')
            else:
                mylocation=os.path.join(destdir,'cluster.yaml')
            dumpobj(wholedict, fmt,mylocation)
            with open(mylocation, "a") as myfile:
                myfile.write("#%s"%(xcatversion))
            print("The cluster inventory data has been dumped to %s"%(mylocation))
        elif destfile:
            dumpobj(wholedict, fmt,destfile)
            with open(destfile, "a") as myfile:
                myfile.write("#%s"%(xcatversion))
            print("The inventory data has been dumped to %s"%(destfile))
        else: 
            if not fmt or fmt.lower() == 'json':
                dump2json(wholedict)
            else:
                dump2yaml(wholedict)
            print("#%s"%(xcatversion))
    dbsession.close() 



def importfromfile(objtypelist, objlist, location,dryrun=None,version=None,update=True):
    dirpath=os.path.dirname(os.path.realpath(location))
    filename=os.path.basename(os.path.realpath(location))
    
    jinjaenv=Environment(loader=FileSystemLoader(dirpath)); 
    jinjasrc=jinjaenv.loader.get_source(jinjaenv,filename)[0]
    jinjatmpl=jinjaenv.get_template(filename)
    jinjast = jinjaenv.parse(jinjasrc)
    jinjavarlist=meta.find_undeclared_variables(jinjast)
    vardict={}
      
    vargitrepo=None
    varswdir=None
    if 'GITREPO' in os.environ.keys():
        vargitrepo=os.environ['GITREPO']
    else:
        oldcwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(location)))
        (retcode,out,err)=runCommand("git rev-parse --show-toplevel")
        if retcode==0:
            vargitrepo=out.strip()
        os.chdir(oldcwd)
    
    if vargitrepo is not None:
        vardict['GITREPO']=vargitrepo
  
    if 'SWDIR' in os.environ.keys():
        varswdir=os.environ['SWDIR']

    if varswdir is not None:
        vardict['SWDIR']=varswdir
    unresolvedvars=list(set(jinjavarlist).difference(set(vardict.keys())))
    if unresolvedvars:
        raise ParseException("unresolved variables in \"%s\": \"%s\", please export them in environment variables"%(location,','.join(unresolvedvars))) 
    
    contents=jinjatmpl.render(vardict) 
 
    envar=''
    if vardict:
        envar=','.join([key+'='+vardict[key] for key in vardict.keys()])
 
    dbsession=DBsession()
    try:
        obj_attr_dict = json.loads(contents)
    except ValueError:
        try: 
            obj_attr_dict = yaml.load(contents)
        except Exception,e:
            raise InvalidFileException("Error: failed to load file \"%s\", please validate the file with 'yamllint %s'(for yaml format) or 'cat %s|python -mjson.tool'(for json format)!"%(location,location,location))
  
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
                raise ObjNonExistException("Error: cannot find %(t)s objects: %(f)s!",t=myobjtype,f=','.join(nonexistobjlist))
            hdl = InventoryFactory.createHandler(myobjtype,dbsession,version)
            if myobjtype not in objfiledict.keys():
                objfiledict[myobjtype]={}
            objfiledict[myobjtype].update(hdl.importObjs(objlist, obj_attr_dict[myobjtype],update,envar))
    else:
        for objtype in obj_attr_dict.keys():#VALID_OBJ_TYPES:
            hdl = InventoryFactory.createHandler(objtype,dbsession,version)
            if objtype not in objfiledict.keys():
                objfiledict[objtype]={}
            objfiledict[objtype].update(hdl.importObjs([], obj_attr_dict[objtype],update,envar))

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
    if os.path.exists(os.path.join(location,'definition.yaml')):
        objfile=os.path.join(location,'definition.yaml')
    elif os.path.exists(os.path.join(location,'definition.json')):
        objfile=os.path.join(location,'definition.json')    
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
            if dryrun:
                print("creating directory: %s. Dryrun mode, do nothing..."%(os.path.dirname(myfile)))
            else:
                try:
                    os.makedirs(os.path.dirname(myfile))
                except OSError, e:
                    if e.errno != os.errno.EEXIST:
                        raise
                    pass
            if os.path.exists(myfile):
                print("Warning: the %s already exists, will be overwritten"%(myfile), file=sys.stderr)
            if os.path.exists(myfile) and os.path.samefile(srcfile,myfile):
                print("Warning: \"%s\" and \"%s\" are the same file, skip copy"%(srcfile,myfile),file=sys.stderr)
            else:
                if dryrun:
                    print("copying file: %s ----> %s. Dryrun mode, do nothing..."%(srcfile,myfile))
                else:
                    shutil.copyfile(srcfile,myfile)
        else:
            print("Warning: the file \""+srcfile+"\" of osimage \""+objname+"\" does not exist!",file=sys.stderr)
    print("The object "+objname+" has been imported")

def importfromdir(location,objtype='osimage',objnamelist=None,dryrun=None,version=None,update=True):
    if not objnamelist:
        objnamelist=os.listdir(location)
    for objname in objnamelist:
        if os.path.exists(os.path.join(location,objname)):
            objdir=os.path.join(location,objname)
            importobjdir(objdir,dryrun,version,update)
        else:
            print("the specified object \""+objname+"\" does not exist under \""+location+"\"!",file=sys.stderr)
     
def importobj(srcfile,srcdir,objtype,objnames=None,dryrun=None,version=None,update=True):
     objtypelist=[]
     importallobjtypes=0
     if objtype:
         objtypelist=[n.strip() for n in objtype.split(',')]
     else:
         importallobjtypes=1

     objnamelist=[]
     if objnames:
         objnamelist=[n.strip() for n in objnames.split(',')]

     if srcfile and os.path.isfile(srcfile):
         importfromfile(objtypelist, objnamelist,srcfile,dryrun,version,update)
     elif srcdir and os.path.isdir(srcdir):
         clusterfile=None
         if os.path.isfile(os.path.join(srcdir,'cluster.yaml')):
             clusterfile=os.path.join(srcdir,'cluster.yaml')
         elif os.path.isfile(os.path.join(srcdir,'cluster.json')):
             clusterfile=os.path.join(srcdir,'cluster.json')

         #this is a cluster inventory directory
         if clusterfile:
             myobjtypelist=[]
             myobjtypelist.extend(objtypelist)

             if 'osimage' in myobjtypelist or importallobjtypes:
                 if 'osimage' in myobjtypelist:
                     myobjtypelist.remove('osimage')
                 if myobjtypelist or importallobjtypes:
                     importfromfile(myobjtypelist,objnamelist,clusterfile,dryrun,version,update)
                 importfromdir(os.path.join(srcdir,'osimage'),'osimage',objnamelist,dryrun,version,update)
             else:
                 importfromfile(objtypelist,objnamelist,clusterfile,dryrun,version,update)
         else:
             objfile=None
             if os.path.isfile(os.path.join(srcdir,'definition.yaml')):
                 objfile=os.path.join(srcdir,'definition.yaml')
             elif os.path.isfile(os.path.join(srcdir,'definition.json')):
                 objfile=os.path.join(srcdir,'definition.json')

             if 'osimage' in objtypelist or importallobjtypes:
                 if objfile:
                     curobjname=os.path.basename(os.path.realpath(srcdir))
                     #this is an osimage derectory
                     if objnames:
                         if curobjname in objnamelist: 
                             importfromdir(srcdir+'/../','osimage',[curobjname],dryrun,version,update)
                             objnamelist.remove(curobjname)
                         if objnamelist:
                             raise InvalidFileException("Error: non-exist objects: \""+','.join(objnamelist)+"\" in inventory directory "+srcdir+"!")        
                     else:
                         #import current object
                         importobjdir(srcdir,dryrun,version,update)
                 else:
                     #this is an osimage inventory directory 
                     importfromdir(srcdir,'osimage',objnamelist,dryrun,version,update)
                 if 'osimage' in objtypelist:
                     objtypelist.remove('osimage')
   
             if objtypelist:
                 raise InvalidFileException("Error: non-exist object types: \""+','.join(objtypelist)+"\" in inventory directory "+srcdir+"!")
          

              
                 
