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

#dbhash={"node1":{"hosts.ip":"10.3.5.21","nodetype.arch":"ppc64","mac.mac":"00:11:22:33:44:55","switch.switch":"sw1","switch.port":"1","postscripts.postscripts":"syslog","nodetype.provmethod":"osimage1","noderes.installnic":"eth0","bootparams.addkcmdline":"rd.break=1","noderes.netboot":"grub2","noderes.xcatmaster":"10.3.5.21"}}

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
            self.__mydict[node]=deepcopy(objdict)
        elif dbhash is not None:
            self.__dbhash[node]=deepcopy(dbhash)
            self.__mydict=deepcopy(Node.__schema)
            self.__mydict[node]=self.__mydict[self.__mydict.keys()[0]]
            del self.__mydict[self.__mydict.keys()[0]]
            self.__deeptraverse(self.name, self.__mydict)

    def __deeptraverse(self, objkey, dict1):
        def action(objkey, dbhash, string):
            if objkey in dbhash.keys() and string in dbhash[objkey]:
                return dbhash[objkey][string]
            else:
                return ''
        for key in dict1.keys():
            if isinstance(dict1[key],dict):
                self.__deeptraverse(objkey,dict1[key])
            else:
                dict1[key]=action(objkey, self.__dbhash, dict1[key])

    def __db2dict(self):
        self.__mydict=deepcopy(Node.__schema)
        self.__mydict[self.name]=self.__mydict[self.__mydict.keys()[0]]
        del self.__mydict[self.__mydict.keys()[0]]
        for key in self.__mydict.keys():
            if isinstance(self.__mydict[key],dict):
                pass

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
        return self.__mydict
    def setobjdict(self,nodedict):
        self.__mydict=deepcopy(nodedict)
    def getdbdata(self):
        return self.__dbhash

if __name__ == "__main__":
    db = dbfactory()
    tabs = ['nodetype', 'switch', 'hosts', 'mac', 'noderes', 'postscripts', 'bootparams']
    nodelist = ['c910f03c17k41','c910f03c17k42']
    obj_attr_dict = db.gettab(tabs, nodelist)

    for node in nodelist:
        obj = Node.createfromdb('c910f03c17k41', dbhash=obj_attr_dict['c910f03c17k41'])
        print(obj.getobjdict())

