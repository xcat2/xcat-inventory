#!/usr/bin/python
import dbobject
from dbobject import *
from dbsession import *


class dbfactory():
    dbsession=None
    def __init__(self):
        self.dbsession=loadSession()
    def gettab(self,tabs,keys=None):    
        if self.dbsession is None:
            return None
        ret={}
        for tabname in tabs:
            if hasattr(dbobject,tabname):
                tab=getattr(dbobject,tabname)
            else:
                continue
            tabkey=tab.getkey()
            if keys is not None and len(keys)!=0:
                tabobj=self.dbsession.query(tab).filter(getattr(tab,tabkey).in_(keys)).all()
            else:
                tabobj=self.dbsession.query(tab).all()
            if not tabobj:
                continue
            for myobj in tabobj:
                mydict=myobj.getdict()
                mynode=mydict[tab.__tablename__+'.'+tabkey]
                if mynode not in ret.keys():
                    ret[mynode]={}
                ret[mynode].update(mydict)
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
                
        if self.dbsession is None or dbdict is None:
            return None
        tabdict={}
        for node in dbdict.keys():
            if node not in tabdict.keys():
                tabdict[node]={}
            nodedict=dbdict[node]
            for tabcol in nodedict.keys():
                (tab,col)=tabcol.split('.')
                if tab not in tabdict[node].keys():
                    tabdict[node][tab]={}
                if tabcol not in tabdict[node][tab].keys():
                    tabdict[node][tab][col]={}
                tabdict[node][tab][col]=nodedict[tabcol]
        for node in tabdict.keys():
            for tab in tabdict[node].keys():
                if hasattr(dbobject,tab):
                    tabcls=getattr(dbobject,tab)
                else:
                    continue
                create_or_update(self.dbsession,tabcls,node,tabdict[node][tab])
            self.dbsession.commit()

if __name__ == "__main__":
    df1=dbfactory()
    mydict=df1.gettab(['mac'],["node0001","node0002"])
    if not mydict:
        mydict={}
        mydict["node0001"]={}
    mydict["node0001"]['mac.comments']="zzzzz"
    mydict["node0001"]['mac.interface']="mmmmmmmmmm"

    df1.settab(mydict)
    mydict1=df1.gettab(['mac'],["node0001"])
    print mydict1
   

