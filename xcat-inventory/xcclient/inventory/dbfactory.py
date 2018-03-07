#!/usr/bin/python
import dbobject
from dbobject import *
from dbsession import DBsession
from sqlalchemy import or_
from xcclient.shell import CommandException

def create_or_update(session,tabcls,key,newdict,ismatrixtable=True):
    tabkey=tabcls.getkey()
    #for matrix table, remove the record if all the non-key values are None or blank 
    delrow=1 
    #for flat table, keep the record untouch if the non-key values are None
    skiprow=1
    for item in newdict.keys():
        if  tabkey != item and newdict[item] is not None:
            skiprow=0        

        if  tabkey != item and newdict[item] is None:
            newdict[item]=''
    
        if tabkey != item and newdict[item]!='':
            delrow=0

        if item == 'disable' and newdict[item]=='':
            newdict[item]=None

    if not ismatrixtable:
        if skiprow:
            return
        #do not remove for flat table
        delrow=0

    try:
        record=session.query(tabcls).filter(getattr(tabcls,tabkey).in_([key])).all()
    except Exception, e:
        raise Exception, "Error: query xCAT table "+tabcls.__tablename__+" failed: "+str(e)
    if record:
        if delrow:
            try:
                session.delete(record[0])
            except Exception, e:
                raise Exception, "Error: delete "+key+" is failed: "+str(e)
            else:
                print("delete row in xCAT table "+tabcls.__tablename__+".")
        else:
           try:
               session.query(tabcls).filter(getattr(tabcls,tabkey) == key).update(newdict)
           except Exception, e:
               raise Exception, "Error: import object "+key+" is failed: "+str(e)
           else:
               print("Import "+key+": update xCAT table "+tabcls.__tablename__+".")
    elif delrow == 0:
        newdict[tabkey]=key
        try:
            session.execute(tabcls.__table__.insert(), newdict)
        except(sqlalchemy.exc.IntegrityError):
            raise CommandException("Error: xCAT object %(t)s is duplicate.", t=key)
        except Exception, e:
            raise Exception, "Error: import object "+key+" is failed: "+str(e) 
        else:
            print("Import "+key+": insert xCAT table "+tabcls.__tablename__+".")

class matrixdbfactory():
    def __init__(self,dbsession):
        self._dbsession=dbsession

    def gettab(self,tabs,keys=None):    
        ret={}
        for tabname in tabs:
           dbsession=self._dbsession.loadSession(tabname); 
           if hasattr(dbobject,tabname):
               tab=getattr(dbobject,tabname)
           else:
               continue
           tabkey=tab.getkey()
           if keys is not None and len(keys)!=0:
               tabobj=dbsession.query(tab).filter(getattr(tab,tabkey).in_(keys),or_(tab.disable == None, tab.disable.notin_(['1','yes']))).all()
           else:
               tabobj=dbsession.query(tab).filter(or_(tab.disable == None, tab.disable.notin_(['1','yes']))).all()
           if not tabobj:
               continue
           for myobj in tabobj:
               mydict=myobj.getdict()
               mykey=mydict[tab.__tablename__+'.'+tabkey]
               if mykey not in ret.keys():
                  ret[mykey]={}
               ret[mykey].update(mydict)
        return  ret 

    def settab(self,tabdict=None):
        #print "=========matrixdbfactory:settab========"
        if tabdict is None:
            return None
        for key in tabdict.keys():
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
                tabkey=tabcls.getkey()
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
        try:
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
        except CommandException as e:
            print str(e)
        except Exception as e:
            print str(e)
            print("import object failed.")
        else:
            print("import object successfully.")          

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
            tabkey=tabcls.getkey()
            ReservedKeys=tabcls.getReservedKeys()
            dbsession=self._dbsession.loadSession(tab)
            try:
                if ReservedKeys:
                    dbsession.query(tabcls).filter(getattr(tabcls,tabkey).notin_(ReservedKeys),or_(tabcls.disable == None, tabcls.disable.notin_(['1','yes']))).delete(synchronize_session='fetch')
                else:
                    dbsession.query(tabcls).filter(or_(tabcls.disable == None, tabcls.disable.notin_(['1','yes']))).delete(synchronize_session='fetch')
            except Exception, e:
                raise Exception, "Error: failed to clear table "+str(tab)+": "+str(e)
            else:
                print("table "+tab+ "cleared!")

if __name__ == "__main__":
     pass
