#!/usr/bin/python
from dbsession import *
from copy import *
import pdb

class mixin(object):
    def getdict(self):
        mydict={}
        for mykey in self.__dict__.keys():
           if mykey in self.__table__.columns:
              mydict[self.__tablename__+'.'+mykey.encode()]= self.__dict__[mykey] if self.__dict__[mykey] is None else self.__dict__[mykey].encode()
        try:
            self.__class__.outprocess(mydict)
        except:
            pass 
        return mydict

########################################################################
class passwd(Base,mixin):
    """"""
    __tablename__ = 'passwd'
    __table_args__ = {'autoload':True}

########################################################################
class networks(Base,mixin):
    """"""
    __tablename__ = 'networks'
    __table_args__ = {'autoload':True}

########################################################################
class nodetype(Base,mixin):
    """"""
    __tablename__ = 'nodetype'
    __table_args__ = {'autoload':True} 

########################################################################
class hosts(Base,mixin):
    """"""
    __tablename__ = 'hosts'
    __table_args__ = {'autoload':True}

########################################################################
class noderes(Base,mixin):
    """"""
    __tablename__ = 'noderes'
    __table_args__ = {'autoload':True}

########################################################################
class switch(Base,mixin):
    """"""
    __tablename__ = 'switch'
    __table_args__ = {'autoload':True}
########################################################################
class mac(Base,mixin):
    """"""
    __tablename__ = 'mac'
    __table_args__ = {'autoload':True}
    @classmethod
    def outprocess(self,mydict):
        key=self.__tablename__+'.'+'mac'
        mydict[key]=mydict[key].split('|')
########################################################################
class postscripts(Base,mixin):
    """"""
    __tablename__ = 'postscripts'
    __table_args__ = {'autoload':True}
    
########################################################################
class bootparams(Base,mixin):
    """"""
    __tablename__ = 'bootparams'
    __table_args__ = {'autoload':True}


#----------------------------------------------------------------------

def query_table_by_node(session, tclass, tkey):
    """"""
    result=session.query(tclass).filter(tclass.node == tkey).all()
    if not result:
       return None 
    return result[0].getdict()


def query_nodelist_by_key(session, nodelist):
    """"""
    nodelist_value = {}
    for node in nodelist:
        nodelist_value[node]={}
        classlist = [Bootparams,Nodetype,Hosts,Switch,Mac,Noderes]
        for eachclass in classlist:
            clsdict = query_table_by_node(session,eachclass,node)
            nodelist_value[node].update(clsdict)
    return nodelist_value

if __name__ == "__main__":

    session = loadSession()
    nodelist_value = {}
    nodelist = ['node0001','node0002']
    nodelist_value = query_nodelist_by_key(session,nodelist)
    print nodelist_value
    session.close()
