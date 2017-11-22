#!/usr/bin/python
import yaml
import json
from copy import *

from dbobject import *
from dbsession import *

#dbhash={"node1":{"hosts.ip":"10.3.5.21","nodetype.arch":"ppc64","mac.mac":"00:11:22:33:44:55","switch.switch":"sw1","switch.port":"1","postscripts.postscripts":"syslog","nodetype.provmethod":"osimage1","noderes.installnic":"eth0","bootparams.addkcmdline":"rd.break=1","noderes.netboot":"grub2","noderes.xcatmaster":"10.3.5.21"}}

class Node():
	__schema=None
        __dbhash=None
	def __init__(self,node,schema=None,dbhash=None):
		self.name=node
                if Node.__schema is None and schema is not None:
			Node.loadschema(schema)
                if Node.__dbhash is None and dbhash is not None:
			Node.loaddb(dbhash)
                #rename the key to the node
		self.__mydict=deepcopy(Node.__schema)
                self.__mydict[self.name]=self.__mydict[self.__mydict.keys()[0]]
                del self.__mydict[self.__mydict.keys()[0]]
		self.__class__.__deeptraverse(self.name,self.__mydict)
        @staticmethod
        def loadschema(schema):
                Node.__schema=yaml.load(file(schema,'r'))
        @staticmethod
        def loaddb(db):
                Node.__dbhash=deepcopy(db)
        @staticmethod
	def listobj():
		return Node.__dbhash.keys()

        @staticmethod 
	def __deeptraverse(objkey,dict1):
		def action(objkey,dbhash,string):
                        if objkey in dbhash.keys() and string in dbhash[objkey]:
				return dbhash[objkey][string]
                        else:
				return ''
		for key in dict1.keys():
	        	if isinstance(dict1[key],dict):
	        		Node.__deeptraverse(objkey,dict1[key]) 
	      		else:
	                        dict1[key]=action(objkey,Node.__dbhash,dict1[key])
        def dump2yaml(self):
		print yaml.dump(self.__mydict,default_flow_style=False)
	def dump2json(self):
		print json.dumps(self.__mydict, sort_keys=True, indent=4, separators=(',', ': '))
        def load(self,filename):
		self.__mydict=yaml.load(file(filename,'r'))			




if __name__ == "__main__":
    session = loadSession()
    nodelist = ['c910f03c17k41','c910f03c17k42']
    nodelist_value = query_nodelist_by_key(session,nodelist)

    Node.loaddb(nodelist_value)
    Node.loadschema('./node.yaml')
    for node in Node.listobj():
	print "==THIS IS YAML=="
    	Node(node).dump2yaml()
	print "==THIS IS JSON=="
    	Node(node).dump2json()

    session.close()

