#!/usr/bin/python
import dbobject
from dbobject import *
from dbsession import *


class dbfactory():
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

    def settab(self,dbdict=None):
        def create_or_update(session,tabcls,key,newdict):
            tabkey=tabcls.getkey()
            record=session.query(tabcls).filter(getattr(tabcls,tabkey).in_([key])).all()
            if record:
                session.query(tabcls).filter(getattr(tabcls,tabkey) == key).update(newdict)
            else:
                print "not found"
                print dbdict
                newdict[tabkey]=key
                session.execute(tabcls.__table__.insert(), newdict)
                session.commit()
                
        if dbdict is None:
            return None
        tabdict={}
        for key in dbdict.keys():
            if key not in tabdict.keys():
                tabdict[key]={}
            curdict=dbdict[key]
            for tabcol in curdict.keys():
                (tab,col)=tabcol.split('.')
                if tab not in tabdict[key].keys():
                    tabdict[key][tab]={}
                if tabcol not in tabdict[key][tab].keys():
                    tabdict[key][tab][col]={}
                tabdict[key][tab][col]=curdict[tabcol]
        for key in tabdict.keys():
            for tab in tabdict[key].keys():
                dbsession=loadSession(tab);
                if hasattr(dbobject,tab):
                    tabcls=getattr(dbobject,tab)
                else:
                    continue
                create_or_update(dbsession,tabcls,key,tabdict[key][tab])
                dbsession.commit()

if __name__ == "__main__":
    df1=dbfactory()
    mydict=df1.gettab(['mac'],["node0001","node0002"])
    print mydict
    if not mydict:
        mydict={}
        mydict["node0001"]={}
    mydict["node0001"]['mac.comments']="kkkkkkkkk"
    mydict["node0001"]['mac.interface']="BBBBBBBBBB"

    df1.settab(mydict)
    mydict1=df1.gettab(['mac'],["node0001"])
    print mydict1
   

