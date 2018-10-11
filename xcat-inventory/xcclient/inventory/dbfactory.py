#!/usr/bin/python
from __future__ import print_function
import dbobject
from dbobject import *
from dbsession import DBsession
from sqlalchemy import or_
#from xcclient.shell import CommandException
from exceptions import *
import utils

def generate_key_dict(tabkeys,inputkeylist):
    keydict={}
    if inputkeylist is None:
        return
    if len(inputkeylist) < len(tabkeys):
        appendtimes=len(tabkeys)-len(inputkeylist)
        while appendtimes > 0:
            inputkeylist.append('')
            appendtimes-=1
    elif len(inputkeylist) > len(tabkeys):
        deducetimes=len(inputkeylist)-len(tabkeys)
        while deducetimes >0:
            inputkeylist[-2]=inputkeylist[-2]+'.'+inputkeylist[-1]
            deducetimes-=1
    keydict=dict(zip(tabkeys,inputkeylist))
    return keydict

def create_or_update(session,tabcls,key,newdict,ismatrixtable=True):
    tabkeys=tabcls.getkeys()
    #for matrix table, remove the record if all the non-key values are None or blank 
    delrow=1 
    #for flat table, keep the record untouch if the non-key values are None
    skiprow=1
    tabcols=tabcls.getcolumns()
    ret_list = list((set(tabkeys).union(set(newdict.keys())))^(set(tabkeys)^set(newdict.keys())))

    for item in newdict.keys():
        if item not in tabcols:
            if newdict[item] is None:
                del newdict[item] 
                continue
            else:
                raise BadSchemaException("Error: no column '"+item+"' in table "+tabcls.__tablename__+", might caused by mismatch between schema version and xCAT version!")
            
        if  item not in tabkeys and newdict[item] is not None:
            skiprow=0        

        if  item not in tabkeys and newdict[item] is None:
            newdict[item]=''
        
        #delete table rows when (1)the key is None or blank (2)the key is not specified in newdict and all non-key values are blank 
        if len(ret_list) is 0:
            if newdict[item]!='': 
                delrow=0
        else:
            for tkey in ret_list:
                if str(newdict[tkey]) !="":
                    delrow=0
        if item == 'disable' and newdict[item]=='':
            newdict[item]=None
   
    if not ismatrixtable:
        if skiprow:
            return
        #do not remove for flat table
        delrow=0
    if key is not None:
        keylist=key.split('.')
    keydict=generate_key_dict(tabkeys,keylist)
    try:
        query=session.query(tabcls)
        for tk in tabkeys:
            query=query.filter(getattr(tabcls,tk).in_(keylist))
        record=query.all()
    except Exception, e:
        raise DBException("Error: query xCAT table "+tabcls.__tablename__+" failed: "+str(e))
    if record:
        if delrow:
            try:
                session.delete(record[0])
            except Exception, e:
                raise DBException("Error: delete "+key+" is failed: "+str(e))
            #else:
            #    print("delete row in xCAT table "+tabcls.__tablename__+".")
        else:
           try:
               query=session.query(tabcls)
               index=0
               for kk in tabkeys:
                   if keylist[index] is not '':
                       query=query.filter(getattr(tabcls,kk) == keylist[index])
                   index+=1
               query.update(newdict)
           except Exception, e:
               raise DBException("Error: import object "+key+" is failed: "+str(e))
           #else:
           #    print("Import "+key+": update xCAT table "+tabcls.__tablename__+".")
    elif delrow == 0:
        finaldict=dict(newdict, **keydict)
        try:
            session.execute(tabcls.__table__.insert(), finaldict)
        except Exception, e:
            raise DBException("Error: import object "+key+" is failed: "+str(e)) 
        #else:
        #    print("Import "+key+": insert xCAT table "+tabcls.__tablename__+".")

class matrixdbfactory():
    def __init__(self,dbsession):
        self._dbsession=dbsession

    def sortdictkeys(self,dbkeys=None,inputkeys=None):
        sortdict={}
        dictvalue=[]
        if inputkeys is None or dbkeys is None:
            return 
        dbkeyslen=len(dbkeys)
        for item in inputkeys:
            each=[]
            each=item.split('.')
            while len(each) < dbkeyslen:
                each.append('')
            dictvalue.append(each)
        index=0
        for key in dbkeys:
            eachvalue=[]
            for item in dictvalue:
                eachvalue.append(item[index])
            index+=1
            sortdict[key]=eachvalue
        return sortdict 

    def gettab(self,tabs,keys=None):    
        ret={}
        for tabname in tabs:
           dbsession=self._dbsession.loadSession(tabname); 
           if hasattr(dbobject,tabname):
               tab=getattr(dbobject,tabname)
           else:
               continue
           tabkeys=tab.getkeys()
           tabdictkey=tab.getdictkey()
           if keys is not None and len(keys)!=0:
               sortdict=self.sortdictkeys(tabkeys,keys)
               if sortdict is not None:
                   query=dbsession.query(tab)
                   for key,value in sortdict.items():
                       query=query.filter(getattr(tab,key).in_(value))
                   query=query.filter(or_(tab.disable == None, tab.disable.notin_(['1','yes'])))        
                   tabobj=query.all()
           else:
               tabobj=dbsession.query(tab).filter(or_(tab.disable == None, tab.disable.notin_(['1','yes']))).all()
           if not tabobj:
               continue
           for myobj in tabobj:
               mydict=myobj.getdict()
               mykey=mydict[tab.__tablename__+'.'+tabdictkey]
               if mykey not in ret.keys():
                  ret[mykey]={}
               ret[mykey].update(mydict)
        return  ret 

    def settab(self,tabdict=None):
        #print "=========matrixdbfactory:settab========"
        #print(tabdict)
        #print("\n")
        if tabdict is None:
            return None
        for key in tabdict.keys():
            utils.verbose("  writting object: "+str(key),file=sys.stdout)
            for tab in tabdict[key].keys():
                dbsession=self._dbsession.loadSession(tab);
                if hasattr(dbobject,tab):
                    tabcls=getattr(dbobject,tab)
                else:
                    continue
                if tabcls.isValid(key,tabdict[key][tab]):
                    create_or_update(dbsession,tabcls,key,tabdict[key][tab])

class flatdbfactory() :
    def __init__(self,dbsession):
        self._dbsession=dbsession

    def gettab(self,tabs,keys=None):    
        ret={}
        if keys:
            rootkey=keys[0]  
        else:
            rootkey='clustersite'
        ret[rootkey]={}
        for tabname in tabs:
            dbsession=self._dbsession.loadSession(tabname);
            if hasattr(dbobject,tabname):
                tab=getattr(dbobject,tabname)
            else:
                continue
            tabobj=dbsession.query(tab).filter(or_(tab.disable == None,tab.disable.notin_(['1','yes']))).all()
            if not tabobj:
                continue
            for myobj in tabobj:
                mydict=myobj.getdict()
                ret[rootkey].update(mydict)
        return  ret
   
    def settab(self,tabdict=None):
        #print "======flatdbfactory:settab======"
        #print tabdict
        if tabdict is None:
            return None
        for key in tabdict.keys():
            for tab in tabdict[key].keys():
                if hasattr(dbobject,tab):
                    tabcls=getattr(dbobject,tab)
                else:
                    continue
                tabkey=tabcls.getdictkey()
                rowentlist=tabcls.dict2tabentry(tabdict[key][tab])
                dbsession=self._dbsession.loadSession(tab)
                for rowent in rowentlist:
                    if tabcls.isValid(key, rowent):
                        create_or_update(dbsession,tabcls,rowent[tabkey],rowent,False)

    

class dbfactory():
    
    def __init__(self,dbsession):
        self._dbsession=dbsession

    def gettab(self,tabs,keys=None):
        flattabs=[]
        matrixtabs=[]
        mydict={}

        for tab in tabs:
            if hasattr(dbobject,tab):
                tabcls=getattr(dbobject,tab)
            else:
                continue       
            if tabcls.getTabtype() == 'flat':
                flattabs.append(tab)
            else:
                matrixtabs.append(tab)
        if flattabs:
            df_flat=flatdbfactory(self._dbsession)
            mydict.update(df_flat.gettab(flattabs,keys))
        if matrixtabs:
            df_matrix=matrixdbfactory(self._dbsession)
            mydict.update(df_matrix.gettab(matrixtabs,keys))
        return mydict
        
                
    def settab(self,dbdict=None):                 
        if dbdict is None:
            return None
        flattabdict={}
        matrixtabdict={}
        #try:
        for key in dbdict.keys():
            curdict=dbdict[key]
            for tabcol in curdict.keys():
                (tab,col)=tabcol.split('.')
                if hasattr(dbobject,tab):
                    tabcls=getattr(dbobject,tab)
                else:
                    continue       
                if tabcls.getTabtype() == 'flat':
                    if key not in flattabdict.keys():
                        flattabdict[key]={}
                    if tab not in flattabdict[key].keys():
                        flattabdict[key][tab]={}
                    if col not in flattabdict[key][tab].keys():
                        flattabdict[key][tab][col]={}
                    flattabdict[key][tab][col]=curdict[tabcol]
                else:
                    if key not in matrixtabdict.keys():
                        matrixtabdict[key]={}
                    if tab not in matrixtabdict[key].keys():
                        matrixtabdict[key][tab]={}
                    if col not in matrixtabdict[key][tab].keys():
                        matrixtabdict[key][tab][col]={}
                    matrixtabdict[key][tab][col]=curdict[tabcol]
        if flattabdict:
            df_flat=flatdbfactory(self._dbsession)
            mydict=df_flat.settab(flattabdict)
        if matrixtabdict: 
            df_matrix=matrixdbfactory(self._dbsession)
            mydict=df_matrix.settab(matrixtabdict)  
        #except Exception as e:
        #  raise ("Error: import object failed.")
        #else:
        #    print("import object successfully.")          

    def cleartab(self,tabs):
        flattabs=[]
        matrixtabs=[]
        for tab in tabs:
            if hasattr(dbobject,tab):
                tabcls=getattr(dbobject,tab)
            else:
                continue       
            if tabcls.getTabtype() == 'flat':
                flattabs.append(tab)
            else:
                matrixtabs.append(tab)
        for tab in matrixtabs:
            if hasattr(dbobject,tab):
                tabcls=getattr(dbobject,tab)
            else:
                continue
            tabkeys=tabcls.getkeys()
            ReservedKeys=tabcls.getReservedKeys()
            dbsession=self._dbsession.loadSession(tab)
            try:
                query=dbsession.query(tabcls)        
                if ReservedKeys:
                    for tk in tabkeys:
                        query=query.filter(getattr(tabcls,tk).notin_(ReservedKeys))
                    query=query.filter(or_(tabcls.disable == None, tabcls.disable.notin_(['1','yes'])))
                    query.delete(synchronize_session='fetch')
                else:
                    dbsession.query(tabcls).filter(or_(tabcls.disable == None, tabcls.disable.notin_(['1','yes']))).delete(synchronize_session='fetch')
            except Exception, e:
                raise DBException("Error: failed to clear table "+str(tab)+": "+str(e))
            #else:
            #    print("table "+tab+ "cleared!")

if __name__ == "__main__":
     pass
