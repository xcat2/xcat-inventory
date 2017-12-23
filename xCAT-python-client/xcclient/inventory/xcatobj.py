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

#remove the dict entries whose value is null or ''
def Util_rmnullindict(mydict):
    for key in mydict.keys():
        if isinstance(mydict[key],dict):
            Util_rmnullindict(mydict[key])
            if not mydict.keys():
                del mydict[key]
        else:
            if not mydict[key]:
                del mydict[key]

# get the dict value mydict[a][b][c] with key path a.b.c
def Util_getdictval(mydict,keystr):
    dictkeyregex=re.compile("([^\.]+)\.?(\S+)*")
    result=re.findall(dictkeyregex,keystr)
    if result:
        (key,remdkey)=result[0]
        if key not in mydict.keys():
            return None
        if remdkey:
            return Util_getdictval(mydict[key],remdkey)
        else:
            return mydict[key]

# get the dict value mydict[a][b][c] with key path a.b.c
def Util_setdictval(mydict,keystr,value):
    dictkeyregex=re.compile("([^\.]+)\.?(\S+)*")
    result=re.findall(dictkeyregex,keystr)
    if result:
        (key,remdkey)=result[0]
        if remdkey:
            if key not in mydict.keys():
                mydict[key]={}      
            Util_setdictval(mydict[key],remdkey,value)
        else:
            mydict[key]=value


class Node():
    __schema=None
    __schema_loc__ = os.path.join(os.path.dirname(__file__), 'node.yaml')

    __depdict_tab=None
    __depdict_val=None

    def __init__(self, node, dbhash=None, objdict=None, schema=None):
        self.name=node
        self.__dbhash = {}
        self.__mydict = {}

        if schema:
            self.__class__.loadschema(schema)
        if objdict is not None:
            self.setobjdict(objdict)
        elif dbhash is not None:
            self.setdbdata(dbhash)

    @classmethod
    def __gendepdict(cls,schmpath):
        valregex=re.compile("^\$\{\{((.*):(.*))\}\}$")
        tabentregex=re.compile("T\{(.*?)\}")
        dictvalregex=re.compile("V\{(.*?)\}")

        rawvalue=Util_getdictval(cls.__schema,schmpath)
        if not rawvalue:
            return False

        cls.__depdict_val[schmpath]={}
        mtchdval=re.findall(valregex,rawvalue)
        if not mtchdval:
            mtchdval=[(':'+rawvalue,'',rawvalue)]
    
        deptablist=[]
        depvallist=[]
        (expression,paramstr,bodystr)=mtchdval[0] 
        if paramstr:
            mtchdtabval=re.findall(tabentregex,paramstr)
            if mtchdtabval:
                deptablist=mtchdtabval
            mtchdval=re.findall(dictvalregex,paramstr)
            if mtchdval:
                depvallist=mtchdval
        if bodystr:
            mtchdtabval=re.findall(tabentregex,bodystr)
            #print "xxxxxxxxxx"
            #print mtchdtabval
            #print "xxxxxxxxxx"
            if mtchdtabval:
                for item in mtchdtabval:
                    cls.__depdict_tab[item]={}
                    cls.__depdict_tab[item]['schmpath']=schmpath
                    cls.__depdict_tab[item]['deptablist']=[]
                    cls.__depdict_tab[item]['deptablist'].extend(deptablist)
                    cls.__depdict_tab[item]['depvallist']=[]
                    cls.__depdict_tab[item]['depvallist'].extend(depvallist)
                    cls.__depdict_tab[item]['expression']=expression


            deptablist.extend(mtchdtabval)
        cls.__depdict_val[schmpath]['depvallist']=[]
        cls.__depdict_val[schmpath]['depvallist'].extend(depvallist)
        cls.__depdict_val[schmpath]['deptablist']=[]
        cls.__depdict_val[schmpath]['deptablist'].extend(deptablist)
        cls.__depdict_val[schmpath]['expression']=expression            

        #print "VVVVVVv"
        #print yaml.dump(cls.__depdict_tab)

        return True


    @classmethod
    def __scanschema(cls,dict1,schmpath=None):
        for key in dict1.keys():
            if schmpath:
                curpath=schmpath+'.'+key
            else:
                curpath=key
            if isinstance(dict1[key],dict):
                cls.__scanschema(dict1[key],curpath)
            else:
                cls.__gendepdict(curpath)
    @classmethod
    def scanschema(cls):
        cls.__depdict_tab={}
        cls.__depdict_val={}
        cls.__scanschema(cls.__schema)
        #print cls.__depdict_tab
        #print cls.__depdict_val
    ''' 
     if key == 'mac' and dict1[key]:
         macregex=re.compile("^\|.*\|.*\|$")
         if not re.match(macregex,dict1[key]):
             dict1[key]=dict1[key].split('|')
    '''
    def __evalschema_tab(self,tabcol):
        mydeptablist=self.__depdict_tab[tabcol]['deptablist']
        mydepvallist=self.__depdict_tab[tabcol]['depvallist']
        myexpression=self.__depdict_tab[tabcol]['expression']
        myschmpath=self.__depdict_tab[tabcol]['schmpath']
        for item in mydepvallist:
            myval=Util_getdictval(self.__mydict,item)
            if myval is None:
                myval=''
            myexpression=myexpression.replace('V{'+item+'}',"'"+myval+"'")
        for item in mydeptablist:
            tabval=''
            if item in self.__dbhash.keys():
                tabval=self.__dbhash[item]
            else:
                tabvol=self.__evalschema_tab(item) 
            myexpression=myexpression.replace('T{'+item+'}',"'"+tabval+"'")   
        tabmatched=re.findall(r'T\{(\S+)\}',myexpression)
        if tabmatched:
            for item in tabmatched:
                myexpression=myexpression.replace('T{'+item+'}',"'"+item+"'")
        evalexp=eval("lambda "+myexpression)
        result=evalexp()
        if 0==cmp(result,tabcol):
            value=Util_getdictval(self.__mydict,myschmpath)
            if value is None:
                value=''
            self.__dbhash[tabcol]=value
        else:
            self.__dbhash[tabcol]=''
        return self.__dbhash[tabcol]
        
    def __evalschema_val(self,valpath):
        mydeptablist=self.__depdict_val[valpath]['deptablist']
        mydepvallist=self.__depdict_val[valpath]['depvallist']
        myexpression=self.__depdict_val[valpath]['expression']
        for item in mydeptablist:    
            tabval=''
            if item in self.__dbhash.keys():
                tabval=self.__dbhash[item]
            if tabval is None:
                tabval=''
            myexpression=myexpression.replace('T{'+item+'}',"'"+tabval+"'")
        for item in mydepvallist:
            myval=Util_getdictval(self.__mydict,item)
            if myval is None:
                myval=self.__evalschema_val(item)
            myexpression=myexpression.replace('V{'+item+'}',"'"+myval+"'")
        evalexp=eval("lambda "+myexpression)
        value=evalexp()
        Util_setdictval(self.__mydict,valpath,value)
        return value 
                   

    def __dict2db(self):
        for key in self.__depdict_tab.keys():
            self.__evalschema_tab(key)
            
    def __db2dict(self):
        for key in self.__depdict_val.keys():
            self.__evalschema_val(key)
        
    @classmethod
    def createfromdb(cls,node, dbhash):
        if not cls.__schema:
            cls.loadschema(cls.__schema_loc__)
        return cls(node, dbhash=dbhash)

    @classmethod
    def createfromfile(cls,node, objdict):
        if not cls.__schema:
            cls.loadschema(cls.__schema_loc__)
        return cls(node, objdict=objdict)

    @classmethod
    def loadschema(cls,schema=None):
        if schema is None:
            schema=Node.__schema_loc__
        cls.__schema=yaml.load(file(schema,'r'))['node']
        cls.scanschema()

    @classmethod
    def gettablist(cls):
        tabdict={}
        for mykey in cls.__depdict_val.keys():
            for tabcol in cls.__depdict_val[mykey]['deptablist']:
                (mytab,mycol)=tabcol.split('.')
                tabdict[mytab]=1
        return tabdict.keys() 
    def getobjdict(self):
        ret={}
        ret[self.name]=deepcopy(self.__mydict)
        Util_rmnullindict(ret[self.name])
        return ret
    def setobjdict(self,nodedict):
        self.__mydict=deepcopy(nodedict)
        self.__dbhash.clear()
        self.__dict2db()
    def getdbdata(self):
        ret={}
        ret[self.name]=deepcopy(self.__dbhash)
        return ret
    def setdbdata(self,dbhash):
        self.__dbhash=deepcopy(dbhash)
        self.__mydict.clear()
        self.__mydict['node']=self.name
        self.__db2dict()

if __name__ == "__main__":

    db = dbfactory()
    Node.loadschema()
    #tabs = ['nodetype', 'switch', 'hosts', 'mac', 'noderes', 'postscripts', 'bootparams']
    tabs=Node.gettablist()
    nodelist = ['node0001']
    #nodelist = ['node0001','c910f03c17k41','c910f03c17k42']
    obj_attr_dict = db.gettab(tabs, nodelist)

    obj={}
    objdict={}
    objdb={}
    for node in nodelist:
        obj[node] = Node.createfromdb(node, dbhash=obj_attr_dict[node])
        objdict.update(obj[node].getobjdict())
        objdb.update(obj[node].getdbdata())
        objdict[node]['device_info']['arch']='x86_64'
        print yaml.dump(obj[node].getobjdict(),default_flow_style=False)


    objdict1={}
    objdb1={}
    for node in nodelist:
        obj[node].setobjdict(objdict[node])
        print obj[node].getobjdict()
        print obj[node].getdbdata()
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
    
