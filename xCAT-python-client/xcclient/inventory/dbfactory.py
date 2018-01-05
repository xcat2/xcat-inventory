#!/usr/bin/python
import dbobject
from dbobject import *
from dbsession import *
from xcclient.shell import CommandException

def create_or_update(session,tabcls,key,newdict):
   '''
   print "=========create_or_update:called========="
   print newdict
   print key
   '''
   tabkey=tabcls.getkey()
   delrow=1 
   for item in newdict.keys():
       if tabkey != item and newdict[item]!='':
           delrow=0
       if item == 'disable' and newdict[item]=='':
           newdict[item]=None
   try:
       record=session.query(tabcls).filter(getattr(tabcls,tabkey).in_([key])).all()
   except:
       raise Exception, "Error: query xCAT table "+tabcls.__tablename__+" failed."
   if record:
       if delrow:
           try:
               session.delete(record[0])
           except:
               raise Exception, "Error: delete "+key+" is failed."
           else:
               print "delete row in xCAT table "+tabcls.__tablename__+"."
       else:
           try:
               session.query(tabcls).filter(getattr(tabcls,tabkey) == key).update(newdict)
           except:
               raise Exception, "Error: import object "+key+" is failed."
           else:
               print "Import "+key+" update xCAT table "+tabcls.__tablename__+"."
   elif delrow == 0:
       newdict[tabkey]=key
       try:
           session.execute(tabcls.__table__.insert(), newdict)
       except(sqlalchemy.exc.IntegrityError):
           raise CommandException("Error: xCAT object %(t)s is duplicate.", t=key)
       except:
           raise Exception, "Error: import object "+key+" is failed."
       else:
           print "Import "+key+": update xCAT table "+tabcls.__tablename__+"."

class matrixdbfactory():
    def gettab(self,tabs,keys=None):    
        ret={}
        for tabname in tabs:
            dbsession=loadSession(tabname); 
            if hasattr(dbobject,tabname):
                tab=getattr(dbobject,tabname)
            else:
                continue
            tabkey=tab.getkey()
            if keys is not None and len(keys)!=0:
                tabobj=dbsession.query(tab).filter(getattr(tab,tabkey).in_(keys)).all()
            else:
                tabobj=dbsession.query(tab).all()
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
        if not isSqlite():
            dbsession=loadSession()
        sessiondict={}
        try:
            for key in tabdict.keys():
                for tab in tabdict[key].keys():
                    if isSqlite():
                        sessiondict[tab]=loadSession(tab);
                        dbsession=loadSession(tab);
                    if hasattr(dbobject,tab):
                        tabcls=getattr(dbobject,tab)
                    else:
                        continue
                    if tabcls.isValid(key,tabdict[key][tab]):
                        create_or_update(dbsession,tabcls,key,tabdict[key][tab])
        except CommandException as e:
            print str(e)
        except Exception as e:
            print str(e)
            print "import object failed."
        else:
            if isSqlite():
                for key in tabdict.keys():
                    for tab in tabdict[key].keys():
                        sessiondict[tab].commit()
            else:
                dbsession.commit()
            print "import object successfully."

class flatdbfactory() :
    def gettab(self,tabs,keys=None):    
        ret={}
        if keys:
            rootkey=keys[0]  
        else:
            rootkey='cluster'

        ret[rootkey]={}
        for tabname in tabs:
            dbsession=loadSession(tabname);
            if hasattr(dbobject,tabname):
                tab=getattr(dbobject,tabname)
            else:
                continue
            tabobj=dbsession.query(tab).all()
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
       if not isSqlite():
           dbsession=loadSession()
       sessiondict={}
       try:
           for key in tabdict.keys():
               for tab in tabdict[key].keys():
                   if isSqlite():
                       sessiondict[tab]=loadSession(tab);
                       dbsession=loadSession(tab);
                   if hasattr(dbobject,tab):
                       tabcls=getattr(dbobject,tab)
                   else:
                       continue
                   tabkey=tabcls.getkey()
                   rowentlist=tabcls.dict2tabentry(tabdict[key][tab])
                   #print rowentlist
                   for rowent in rowentlist:
                       if tabcls.isValid(key, rowent):
                           create_or_update(dbsession,tabcls,rowent[tabkey],rowent)
       except CommandException as e:
           print str(e)
       except Exception as e:
           print str(e)
           print "import object failed."
       else:
           if isSqlite():
               for key in tabdict.keys():
                   for tab in tabdict[key].keys():
                       sessiondict[tab].commit()
           else:
               dbsession.commit()
           print "import object successfully."
class dbfactory():
    _dbfactoryoftab={'site':'flat'}
    def gettab(self,tabs,keys=None):
        flattabs=[]
        matrixtabs=[]
        mydict={}
        for tab in tabs:
            if tab in self._dbfactoryoftab.keys() and self._dbfactoryoftab[tab] == 'flat':
                flattabs.append(tab)
            else:
                matrixtabs.append(tab)
        if flattabs:
            df_flat=flatdbfactory()
            mydict.update(df_flat.gettab(flattabs,keys))
        if matrixtabs:
            df_matrix=matrixdbfactory()
            mydict.update(df_matrix.gettab(matrixtabs,keys))
        return mydict
        
                
    def settab(self,dbdict=None):                 
        if dbdict is None:
            return None
        flattabdict={}
        matrixtabdict={}
        for key in dbdict.keys():
            curdict=dbdict[key]
            for tabcol in curdict.keys():
                (tab,col)=tabcol.split('.')
                if tab in self._dbfactoryoftab.keys() and self._dbfactoryoftab[tab] == 'flat':
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
            df_flat=flatdbfactory()
            mydict=df_flat.settab(flattabdict)
        if matrixtabdict: 
            df_matrix=matrixdbfactory()
            mydict=df_matrix.settab(matrixtabdict)            

if __name__ == "__main__":
    df0=flatdbfactory()
    mydict=df0.gettab(['site'])
    print mydict
    exit()

    df1=dbfactory()
    mydict=df1.gettab(['mac'],["node0001","node0002"])
    print mydict
    exit()
    if not mydict:
        mydict={}
        mydict["node0001"]={}
    mydict["node0001"]['mac.comments']="kkkkkkkkk"
    mydict["node0001"]['mac.interface']="BBBBBBBBBB"
    df1.settab(mydict)
    mydict1=df1.gettab(['mac'],["node0001"])
    print mydict1

    mydict3=df1.gettab(['networks'],["mgtnetwork"])
    print mydict3
   
    mydict3={}
    mydict3["hpctest1"]={}
    mydict3["hpctest1"]['networks.net']="70.0.0.0"
    df1.settab(mydict3)

    mydict3={}
    mydict3["hpctest2"]={}
    mydict3["hpctest2"]['networks.mask']="255.0.0.0"
    df1.settab(mydict3)

    mydict3={}
    mydict3["hpctest3"]={}
    mydict3["hpctest3"]['networks.net']="70.0.0.0"
    mydict3["hpctest3"]['networks.mask']="255.0.0.0"
    df1.settab(mydict3)

