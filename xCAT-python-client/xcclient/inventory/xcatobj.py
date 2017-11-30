#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#
import yaml
import json
import re
from copy import *

from dbobject import *
from dbfactory import *

import pdb

class Node():
    __schema=None
    __schema_loc__ = os.path.join(os.path.dirname(__file__), 'node.yaml')

    def __init__(self, node, dbhash=None, objdict=None, schema=None):
        self.name=node
        self.__dbhash = {}
        self.__mydict = {}

        if schema:
            Node.loadschema(schema)
        if objdict is not None:
            self.setobjdict(objdict)
        elif dbhash is not None:
            self.setdbdata(dbhash)

    def __parseschmaval(self,rawvalue,onlytabcol=0):

        if rawvalue is None:
            return None

        evalregex=re.compile("(VAL=)?\s*(.+)")
        subregx=re.compile("(\S+)(?:\s*if\s*\((\S+)\s*==\s*(\S+)\))?")
        valregex=re.compile("'(\S+)'")
        tabcolregex=re.compile("\S+\.\S+")
        dictkeyregex=re.compile("\[(\S+?)\](\S+)*")
       
        (valtype,schmvalue)=re.findall(evalregex,rawvalue)[0]
        if not valtype:
            if re.match(tabcolregex,schmvalue):
                if onlytabcol:  
                    return schmvalue
                else:
                    try:
                        return self.__dbhash[schmvalue]
                    except KeyError:
                        return None
            else:
                if onlytabcol:
                    return None
                else:
                    return schmvalue   

        dbkey=''

        for subex in schmvalue.split(';'):
            (value,condkey,condval)=re.findall(subregx,subex)[0]
            if value and ( not condkey or not condval):
                dbkey=value
                break
            if re.match(tabcolregex,condkey):
                if condkey in self.__dbhash.keys() and self.__dbhash[condkey]:
                    condkey=self.__dbhash[condkey]
                else:
                    condkey=''
            else: 
                if re.match(dictkeyregex,condkey):
                    def __getdictval(mydict,keystr):
                        result=re.findall(dictkeyregex,keystr)
                        if result:
                            if result[0][1]:
                                return __getdictval(mydict[result[0][0]],result[0][1])
                            else:
                                return mydict[result[0][0]]
                        else: 
                            return None
                    condkey=__getdictval(self.__schema['node'],condkey)
                    if condkey:
                        condkey=self.__parseschmaval(condkey)

            #valmatch=re.findall(valregex,value)
            #if valmatch:
            #    value=valmatch[0]

            condvalmatch=re.findall(valregex,condval)
            if condvalmatch:
                condval=condvalmatch[0]
            else:
                if condval == 'node':
                    condval=self.name

            if condkey and condkey == condval:
                dbkey = value
                break
            else:
                continue

        import pdb
        #if 'servicenode.node' in schmvalue:
        #    pdb.set_trace()

        dbkeymatch=re.findall(valregex,dbkey)
        if dbkeymatch:
            if onlytabcol:
                return None
            else:
                return dbkeymatch[0]         
        else: 
            if re.match(tabcolregex,dbkey):
                if onlytabcol: 
                    return  dbkey
                else:
                    return self.__dbhash[dbkey]

    def __db2dict(self, dict1):
        for key in dict1.keys():
            if isinstance(dict1[key],dict):
                self.__db2dict(dict1[key])
                if not dict1[key].keys():
                    del dict1[key]
            else: 
                value=self.__parseschmaval(dict1[key])
                if not value:
                    del dict1[key]
                else:
                    dict1[key]=value
                if key == 'mac' and dict1[key]:
                    macregex=re.compile("^\|.*\|.*\|$")
                    if not re.match(macregex,dict1[key]):
                        dict1[key]=dict1[key].split('|')

    def __dict2db(self,objdict,schemadict):
        for key in objdict.keys():
            if isinstance(objdict[key],dict):
                self.__dict2db(objdict[key],schemadict[key])
            else:
                tabcol=self.__parseschmaval(schemadict[key],onlytabcol=1)
                if not tabcol: 
                    continue
                if tabcol == 'mac.mac':
                    self.__dbhash[tabcol]='|'.join(objdict[key])
                else:
                    self.__dbhash[tabcol]=objdict[key]
        
    @staticmethod
    def createfromdb(node, dbhash):
        if not Node.__schema:
            Node.loadschema(Node.__schema_loc__)
        return Node(node, dbhash=dbhash)

    @staticmethod
    def createfromfile(node, objdict):
        if not Node.__schema:
            Node.loadschema(Node.__schema_loc__)
        return Node(node, objdict=objdict)

    @staticmethod
    def loadschema(schema=None):
        if schema is None:
            schema=Node.__schema_loc__
        Node.__schema=yaml.load(file(schema,'r'))

    @staticmethod
    def gettablist():
        def __gettablist(schemadict,tabdict):
            regx=re.compile("(VAL=)?\s*(.+)")
            subregx=re.compile("(\S+)(?:\s*if\s*\((\S+)\s*==\s*(\S+)\))?")
            valregex=re.compile("'(\S+)'")
            for key in schemadict.keys():
                if isinstance(schemadict[key],dict):
                    __gettablist(schemadict[key],tabdict)
                else:
                    tabcolmatch=re.findall(regx,schemadict[key])                    
                    if tabcolmatch:
                        (valtype,conds)=tabcolmatch[0]
                        if valtype == 'VAL=':
                            for cond in conds.split(';'):
                                (value,condkey,condval)=re.findall(subregx,cond)[0] 
                                if not re.findall(valregex,value):
                                    tabdict[value.split('.')[0]]=1
                        else:        
                            tabdict[schemadict[key].split('.')[0]]=1
        tabdict={}
        __gettablist(Node.__schema,tabdict) 
        return tabdict.keys()
    def getobjdict(self):
        ret={}
        ret[self.name]=deepcopy(self.__mydict)
        return ret
    def setobjdict(self,nodedict):
        self.__mydict=deepcopy(nodedict)
        self.__dbhash.clear()
        self.__dict2db(self.__mydict, Node.__schema['node'])
    def getdbdata(self):
        ret={}
        ret[self.name]=deepcopy(self.__dbhash)
        return ret
    def setdbdata(self,dbhash):
        self.__dbhash=deepcopy(dbhash)
        self.__mydict.clear()
        self.__mydict=deepcopy(Node.__schema['node'])
        self.__db2dict(self.__mydict)

if __name__ == "__main__":
    db = dbfactory()
    tabs = ['nodetype', 'switch', 'hosts', 'mac', 'noderes', 'postscripts', 'bootparams']
    nodelist = ['c910f03c17k41','c910f03c17k42']
    obj_attr_dict = db.gettab(tabs, nodelist)

    obj={}
    objdict={}
    objdb={}
    for node in nodelist:
        obj[node] = Node.createfromdb(node, dbhash=obj_attr_dict[node])
        objdict.update(obj[node].getobjdict())
        objdb.update(obj[node].getdbdata())
        objdict[node]['device_info']['arch']='x86_64'

    objdict1={}
    objdb1={}
    for node in nodelist:
        obj[node].setobjdict(objdict[node])
        objdict1.update(obj[node].getobjdict())
        objdb1.update(obj[node].getdbdata())
        objdb1[node]['nodetype.arch']="armv71"
      
    objdb2={}
    objdict2={}
    for node in nodelist:
        obj[node].setdbdata(objdb1[node])
        objdict2.update(obj[node].getobjdict())
        objdb2.update(obj[node].getdbdata())

    print "========="
    print yaml.dump(objdict2,default_flow_style=False)
    print "========="
    print yaml.dump(objdb2,default_flow_style=False)
    print "========="
    
    Node.loadschema()
    for i in  Node.gettablist():
        print i
    
