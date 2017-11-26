#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#
import yaml
import json
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
            self.__mydict=deepcopy(objdict)
            self.__dbhash.clear()
            self.__dict2db(self.__mydict,Node.__schema['node'])
        elif dbhash is not None:
            self.__dbhash=deepcopy(dbhash)
            self.__mydict.clear()
            self.__mydict=deepcopy(Node.__schema['node'])
            self.__db2dict(self.__mydict)

    def __db2dict(self, dict1):
        for key in dict1.keys():
            if isinstance(dict1[key],dict):
                self.__db2dict(dict1[key])
            else: 
                dbkey=dict1[key]
                if dbkey in self.__dbhash.keys():
                     dict1[key]=self.__dbhash[dbkey]
                else:
                     dict1[key]=''

    def __dict2db(self,objdict,schemadict):
        for key in objdict.keys():
            if isinstance(objdict[key],dict):
                self.__dict2db(objdict[key],schemadict[key])
            else:
                self.__dbhash[schemadict[key]]=objdict[key]

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
    def loadschema(schema):
        Node.__schema=yaml.load(file(schema,'r'))

    def listobj(self):
        return self.__dbhash.keys()

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
        #pdb.set_trace()
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


    
