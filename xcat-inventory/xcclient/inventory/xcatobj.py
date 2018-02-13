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
from exceptions import *
import vutil
import pdb

#remove the dict entries whose value is null or ''
def Util_rmnullindict(mydict):
    for key in mydict.keys():
        if isinstance(mydict[key],dict):
            Util_rmnullindict(mydict[key])
            if not mydict[key].keys():
                del mydict[key]
        else:
            if not mydict[key]:
                del mydict[key]



# get the dict value mydict[a][b][c] with key path a.b.c
def Util_getdictval(mydict,keystr):
    if not  isinstance(mydict,dict):
        return None
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


class XcatBase(object):
    _schema=None
    _schema_loc__ = None

    _depdict_tab=None
    _depdict_val=None

    def __init__(self, objname, dbhash=None, objdict=None, schema=None):
        self.name=objname
        self._dbhash = {}
        self._mydict = {}

        if schema:
            self.__class__.loadschema(schema)
        if objdict is not None:
            self.setobjdict(objdict)
        elif dbhash is not None:
            self.setdbdata(dbhash)

    @classmethod
    def __gendepdict(cls,schmpath):
        valregex=re.compile("^\$\{\{((.*):(.*))\}\}\s*$")
        revregex=re.compile("^W:T\{(\S+)\}=(.+)$")
        validateregex=re.compile("^C:(.+)$")
        tabentregex=re.compile("T\{(.*?)\}")
        dictvalregex=re.compile("V\{(.*?)\}")
    
        def __parselambda(expression):
            mtchdval=re.findall(valregex,expression)
            if not mtchdval:
                mtchdval=[(':'+expression,'',expression)]
            ret={}
            ret['tabsinparam']=[]
            ret['tabsinbody']=[]
            ret['valsinparam']=[]
            ret['valsinbody']=[]
            ret['expression']=[]

            (expression,paramstr,bodystr)=mtchdval[0]
            if expression:
                ret['expression']=expression
            if paramstr:
                mtchdtabval=re.findall(tabentregex,paramstr)
                if mtchdtabval:
                    ret['tabsinparam'].extend(mtchdtabval)
                mtchdval=re.findall(dictvalregex,paramstr)
                if mtchdval:
                    ret['valsinparam'].extend(mtchdval)
            if bodystr:
                mtchdtabval=re.findall(tabentregex,bodystr)
                if mtchdtabval:
                    ret['tabsinbody'].extend(mtchdtabval)
                mtchdval=re.findall(dictvalregex,bodystr)
                if mtchdval:
                    ret['valsinbody'].extend(mtchdval)                
            return ret

       
        rawvalue=Util_getdictval(cls._schema,schmpath)
        if not rawvalue:
            return False
        if isinstance(rawvalue,list):
            rawvaluelist=rawvalue
        else:
            rawvaluelist=[rawvalue]  
        cls._depdict_val[schmpath]={}
       
        fwdrules=[] 
        revrules=[]
        validaterules=[]
        for item in rawvaluelist:
            if not re.match(valregex,item) and not re.match(revregex,item) and not re.match(validateregex,item):
                item='${{:'+item+'}}'
                fwdrules.append(item)
            elif re.match(valregex,item): 
                fwdrules.append(item)
            elif re.match(revregex,item):
                revrules.append(item)
            elif re.match(validateregex,item):
                validaterules.append(item)

        cls._depdict_val[schmpath]['validate']={}
        cls._depdict_val[schmpath]['validate']['depvallist']=[]
        cls._depdict_val[schmpath]['validate']['expression']=[]
        for item in validaterules:
            myexpression=re.findall(validateregex,item)[0] 
            ret=__parselambda(myexpression)
            cls._depdict_val[schmpath]['validate']['expression'].append(ret['expression'])
            cls._depdict_val[schmpath]['validate']['depvallist'].extend(ret['valsinparam'])
            cls._depdict_val[schmpath]['validate']['depvallist'].extend(ret['valsinbody'])

        for item in fwdrules:
            ret=__parselambda(item)
            cls._depdict_val[schmpath]['depvallist']=[]
            cls._depdict_val[schmpath]['depvallist'].extend(ret['valsinparam'])
            cls._depdict_val[schmpath]['deptablist']=[]
            cls._depdict_val[schmpath]['deptablist'].extend(ret['tabsinparam'])
            cls._depdict_val[schmpath]['deptablist'].extend(ret['tabsinbody'])
            cls._depdict_val[schmpath]['expression']=ret['expression']    
           
            for tabcol in ret['tabsinbody']:
                cls._depdict_tab[tabcol]={} 
                cls._depdict_tab[tabcol]['schmpath']=schmpath
                cls._depdict_tab[tabcol]['deptablist']=[]
                cls._depdict_tab[tabcol]['deptablist'].extend(ret['tabsinparam'])
                cls._depdict_tab[tabcol]['depvallist']=[]
                cls._depdict_tab[tabcol]['depvallist'].extend(ret['valsinparam'])
                cls._depdict_tab[tabcol]['expression']=ret['expression']

        for item in revrules:
             (tabcol,myexpression)=re.findall(revregex,item)[0]
             ret=__parselambda(myexpression)
             cls._depdict_tab[tabcol]={} 
             cls._depdict_tab[tabcol]['expression']=ret['expression']
             cls._depdict_tab[tabcol]['deptablist']=[]
             cls._depdict_tab[tabcol]['deptablist'].extend(ret['tabsinparam'])
             cls._depdict_tab[tabcol]['deptablist'].extend(ret['tabsinbody'])
             cls._depdict_tab[tabcol]['depvallist']=[]
             cls._depdict_tab[tabcol]['depvallist'].extend(ret['valsinparam'])
             cls._depdict_tab[tabcol]['depvallist'].extend(ret['valsinbody'])
             cls._depdict_tab[tabcol]['schmpath']=''
                
        return True

    @classmethod
    def __scanschema(cls,schmdict,schmpath=None):
        for key in schmdict.keys():
            if schmpath:
                curpath=schmpath+'.'+key
            else:
                curpath=key
            if isinstance(schmdict[key],dict):
                cls.__scanschema(schmdict[key],curpath)
            else:
                cls.__gendepdict(curpath)
    @classmethod
    def scanschema(cls):
        cls._depdict_tab={}
        cls._depdict_val={}
        cls.__scanschema(cls._schema)
        #print yaml.dump(cls._depdict_tab,default_flow_style=False)
        #print yaml.dump(cls._depdict_val,default_flow_style=False)

    def __evalschema_tab(self,tabcol):
        mydeptablist=self._depdict_tab[tabcol]['deptablist']
        mydepvallist=self._depdict_tab[tabcol]['depvallist']
        myexpression=self._depdict_tab[tabcol]['expression']
        myschmpath=self._depdict_tab[tabcol]['schmpath']
        for item in mydepvallist:
            myval=Util_getdictval(self._mydict,item)
            if myval is None:
                myval=''
            myexpression=myexpression.replace('V{'+item+'}',"'"+myval+"'")
        for item in mydeptablist:
            tabval=''
            if item in self._dbhash.keys():
                tabval=self._dbhash[item]
            else:
                tabvol=self.__evalschema_tab(item) 
            myexpression=myexpression.replace('T{'+item+'}',"'"+tabval+"'")   
        tabmatched=re.findall(r'T\{(\S+)\}',myexpression)
        if tabmatched:
            for item in tabmatched:
                if myschmpath: 
                    myexpression=myexpression.replace('T{'+item+'}',"'"+item+"'")
                else:
                    tabvol=self.__evalschema_tab(item)
                    myexpression=myexpression.replace('T{'+item+'}',"'"+tabval+"'")
        #print "lambda "+myexpression
        evalexp=eval("lambda "+myexpression)
        result=evalexp()
        if myschmpath:
            if 0==cmp(result,tabcol):
                value=Util_getdictval(self._mydict,myschmpath)
                if value is None:
                    value=''
                self._dbhash[tabcol]=value
            else:
                self._dbhash[tabcol]=''
            return self._dbhash[tabcol]
        else:
            self._dbhash[tabcol]=result
        
    def __evalschema_val(self,valpath):
        mydeptablist=self._depdict_val[valpath]['deptablist']
        mydepvallist=self._depdict_val[valpath]['depvallist']
        myexpression=self._depdict_val[valpath]['expression']
        for item in mydeptablist:    
            tabval=''
            if item in self._dbhash.keys():
                tabval=self._dbhash[item]
            if tabval is None:
                tabval=''
            myexpression=myexpression.replace('T{'+item+'}',"'"+tabval+"'")
        for item in mydepvallist:
            myval=Util_getdictval(self._mydict,item)
            if myval is None:
                myval=self.__evalschema_val(item)
                if myval is None:
                    myval=''
            myexpression=myexpression.replace('V{'+item+'}',"'"+myval+"'")
        try:
            evalexp=eval("lambda "+myexpression)
            value=evalexp()
        except Exception,e:
            raise  InvalidValueException("Error: failed to process schema entry ["+valpath+"]: \""+myexpression+"\"")
        Util_setdictval(self._mydict,valpath,value)
        return value 
                   

    def __dict2db(self):
        for key in self._depdict_tab.keys():
            self.__evalschema_tab(key)
            
    def __db2dict(self):
        for key in self._depdict_val.keys():
            self.__evalschema_val(key)
        
    @classmethod
    def createfromdb(cls,objname, dbhash):
        if not cls._schema:
            cls.loadschema(cls._schema_loc__)
        return cls(objname, dbhash=dbhash)

    @classmethod
    def createfromfile(cls,objname, objdict):
        if not cls._schema:
            cls.loadschema(cls._schema_loc__)
        return cls(objname, objdict=objdict)

    @classmethod
    def loadschema(cls,schema=None):
        if schema is None:
            schema=cls._schema_loc__
        #cls._schema=yaml.load(file(schema,'r'))['node']
        try: 
            schema=yaml.load(file(schema,'r'))
        except Exception, e:
            raise BadSchemaException("Error: Invalid schema file \""+schema+"\"!") 
        schmkey=schema.keys()[0]
        cls._schema=schema[schmkey] 
        cls.scanschema()
        cls._schema_loc__=schema

    @classmethod
    def gettablist(cls):
        tabdict={}
        for mykey in cls._depdict_val.keys():
            for tabcol in cls._depdict_val[mykey]['deptablist']:
                (mytab,mycol)=tabcol.split('.')
                tabdict[mytab]=1
        return tabdict.keys() 

    def getobjdict(self):
        ret={}
        ret[self.name]=deepcopy(self._mydict)
        Util_rmnullindict(ret[self.name])
        del ret[self.name]['obj_name']
        return ret
  
  

    def validatelayout(self,objdict):
        def _dictcmp(schemadict,objdict,invalidkeylist,curpath=''):
           if isinstance(objdict,dict):
               if not isinstance(schemadict,dict):
                   invalidkeylist.append(curpath)
                   return
               for key in objdict.keys():
                   if schemadict.has_key(key):
                       _dictcmp(schemadict[key],objdict[key],invalidkeylist,curpath+'.'+key)
                   else:
                       invalidkeylist.append(curpath+'.'+key)
           else:
               pass

        if not isinstance(objdict,dict):
            raise InvalidFileException("Error: invalid object definition of "+slef.name)
        
        invalidkeylist=[]
        _dictcmp(self.__class__._schema,objdict,invalidkeylist)
        if invalidkeylist:
            raise InvalidFileException("Error: invalid keys \""+','.join(invalidkeylist)+"\" found in object definition of "+self.name)

        return       
        
    def validatevalue(self,objdict):
        for key in self._depdict_val.keys():
            depvallist=self._depdict_val[key]['validate']['depvallist']
            expression=self._depdict_val[key]['validate']['expression']
            for myexpression in expression:
                for val in depvallist:
                    myval=Util_getdictval(objdict,val)
                    if myval is None:
                        myval=''
                    myexpression=myexpression.replace('V{'+val+'}',"'"+str(myval)+"'")                    
                try:
                    #print myexpression
                    evalexp=eval("lambda "+myexpression)
                    value=evalexp()
                except Exception,e:                    
                    raise  InvalidValueException("Error: encountered some error when validate schema entry ["+key+"]: "+str(e)) 
                if not value:
                    raise  InvalidValueException("Error: failed to validate schema entry ["+key+"]: \""+myexpression+"\"") 


    def setobjdict(self,objdict):
        self.validatelayout(objdict)
        self.validatevalue(objdict)
        self._mydict=deepcopy(objdict)
        self._mydict['obj_name']=self.name
        self._dbhash.clear()
        self.__dict2db()

    def getdbdata(self):
        ret={}
        ret[self.name]=deepcopy(self._dbhash)
        return ret

    def setdbdata(self,dbhash):
        self._dbhash=deepcopy(dbhash)
        self._mydict.clear()
        self._mydict['obj_name']=self.name
        self.__db2dict()


class Node(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/node.yaml')
    def getobjdict(self):
        ret={}
        ret=super(Node,self).getobjdict()
        macpath=""
        nicspath=""
        for item in Node._depdict_val.keys():
            if re.match(r'^\S+\.mac$',item):
                macpath=item
            matchedpath=re.findall(r'^(\S+\.nics)\.\S+$',item)
            if matchedpath:
                nicspath=matchedpath[0]
            if macpath and nicspath:
                break
        if macpath:
            mac=Util_getdictval(self._mydict,macpath)
            if mac and not isinstance(mac,list):
                if re.match(r'[^\|]\S+[^\|]$',mac):
                    Util_setdictval(ret[self.name],macpath,mac.split('|'))
                else:
                    Util_setdictval(ret[self.name],macpath,[mac])
        if nicspath:
            rawnicsdict=Util_getdictval(ret[self.name],nicspath)
            if rawnicsdict:
                nicsdict={}
                for key in rawnicsdict.keys():
                    rawvaluelist=rawnicsdict[key].split(',')
                    for nicent in rawvaluelist:
                        try:
                            (nic,attrstr)=nicent.split('!')
                            if nic not in nicsdict.keys():
                                nicsdict[nic]={}
                            if re.match(r'^[^\|]\S+\|\S+[^\|]$',attrstr):
                                nicsdict[nic][key]=attrstr.split('|')
                            else:
                                nicsdict[nic][key]=[attrstr]
                        except Exception,e:
                            raise InvalidValueException("Error: invalid value \""+nicent+"\" for object "+self.name+" found "+"in nics table") 
                Util_setdictval(ret[self.name],nicspath,nicsdict)
        return ret

    def setobjdict(self,objdict):
        tmpdict=deepcopy(objdict)
        macpath=""
        nicspath=""
        for item in Node._depdict_val.keys():
            if re.match(r'^\S+\.mac$',item):
                macpath=item
            matchedpath=re.findall(r'^(\S+\.nics)\.\S+$',item)
            if matchedpath:
                nicspath=matchedpath[0]
            if macpath and nicspath:
                break
        if macpath:
            mac=Util_getdictval(tmpdict,macpath)
        if mac and isinstance(mac,list):
            Util_setdictval(tmpdict,macpath,'|'.join(mac))         
        if nicspath:
            nicattrstr=''
            nicsattrdict={}
            rawnicsdict=Util_getdictval(tmpdict,nicspath)
            if rawnicsdict:
                for nic in rawnicsdict.keys():
                    nicattr=rawnicsdict[nic]
                    for attr in nicattr.keys():
                         if attr not in nicsattrdict.keys():
                             nicsattrdict[attr]=[]
                         nicsattrdict[attr].append(nic+'!'+'|'.join(nicattr[attr]))
                for item in nicsattrdict.keys():
                    nicsattrdict[item]=','.join(nicsattrdict[item])
                Util_setdictval(tmpdict,nicspath,nicsattrdict)
        super(Node,self).setobjdict(tmpdict)
    
class Osimage(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/osimage.yaml')
    
class Network(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/network.yaml')

class Route(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/route.yaml')

class Policy(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/policy.yaml')

class Passwd(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/passwd.yaml')

class Site(XcatBase):
    _schema_loc__ = os.path.join(os.path.dirname(__file__), 'schema/latest/site.yaml')

if __name__ == "__main__":

    db = dbfactory()
    Node.loadschema()
    Osimage.loadschema()
    Network.loadschema()
    Route.loadschema()
    tabs=Network.gettablist()
    networklist=['192_168_11_0-255_255_255_0']
    obj_attr_dict =db.gettab(tabs,networklist)
    obj={}
    objdict={}
    objdb={}
    for item in networklist:
        obj[item] = Network.createfromdb(item, dbhash=obj_attr_dict[item])
        objdict.update(obj[item].getobjdict())
        objdb.update(obj[item].getdbdata())
        print yaml.dump(obj[item].getobjdict(),default_flow_style=False)
    '''
    tabs=Route.gettablist()
    routelist=['20net']
    obj_attr_dict =db.gettab(tabs,routelist)
    obj={}
    objdict={}
    objdb={}
    for item in routelist:
        obj[item] = Route.createfromdb(item, dbhash=obj_attr_dict[item])
        objdict.update(obj[item].getobjdict())
        objdb.update(obj[item].getdbdata())
        print yaml.dump(obj[item].getobjdict(),default_flow_style=False)

    exit()
    '''
    tabs=Osimage.gettablist()
    osimagelist=['rhels7.4-ppc64le-install-compute']
    obj_attr_dict =db.gettab(tabs,osimagelist)
    obj={}
    objdict={}
    objdb={}
    for item in osimagelist:
        obj[item] = Osimage.createfromdb(item, dbhash=obj_attr_dict[item])
        objdict.update(obj[item].getobjdict())
        objdb.update(obj[item].getdbdata())
        print yaml.dump(obj[item].getobjdict(),default_flow_style=False)

    #exit()
    #tabs = ['nodetype', 'switch', 'hosts', 'mac', 'noderes', 'postscripts', 'bootparams']
    tabs=Node.gettablist()
    #nodelist = ['node0001','testng1']
    nodelist = ['bybc0607']
    #nodelist = ['node0001','c910f03c17k41','c910f03c17k42']
    obj_attr_dict = db.gettab(tabs, nodelist)

    obj={}
    objdict={}
    objdb={}
    for node in nodelist:
        obj[node] = Node.createfromdb(node, dbhash=obj_attr_dict[node])
        objdict.update(obj[node].getobjdict())
        objdb.update(obj[node].getdbdata())
        #objdict[node]['device_info']['arch']='x86_64'
        #objdict[node]['device_info']['disksize']='200'
        print yaml.dump(obj[node].getobjdict(),default_flow_style=False)

    objdict1={}
    objdb1={}
    for node in nodelist:
        obj[node].setobjdict(objdict[node])
        objdict1.update(obj[node].getobjdict())
        print yaml.dump(obj[node].getobjdict(),default_flow_style=False)
        objdb1.update(obj[node].getdbdata())
        objdb1[node]['nodetype.arch']="armv71"
    objdb2={}
    objdict2={}
    for node in nodelist:
        print yaml.dump(objdb1,default_flow_style=False)
        obj[node].setdbdata(objdb1[node])
        objdict2.update(obj[node].getobjdict())
        objdb2.update(obj[node].getdbdata())

    print "========="
    print yaml.dump(objdict2,default_flow_style=False)
    print "========="
    print yaml.dump(objdb2,default_flow_style=False)
    print "========="
    
    
