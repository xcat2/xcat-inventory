#!/usr/bin/python
from dbsession import *
from copy import *
from sqlalchemy import inspect
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

    @classmethod
    def getkey(cls):
        ins = inspect(cls)
        return ins.primary_key[0].key

    @classmethod
    def isValid(cls, netname, tabdict):
        return True

########################################################################
class passwd(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('passwd')
    __tablename__ = 'passwd'
    __table_args__ = {'autoload':True}

########################################################################
class networks(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('networks')
    __tablename__ = 'networks'
    __table_args__ = {'autoload':True}

    @classmethod
    def getkey(cls):
        return 'netname'

    @classmethod    
    def isValid(cls, netname, tabdict):
        eptkey=0
        if 'net' not in tabdict.keys():
            print "Error: net value should not be empty for xCAT network object "+netname
            eptkey=1
        if 'mask' not in tabdict.keys():
            print "Error: mask value should not be empty for xCAT network object "+netname
            eptkey=1
        if eptkey:
            return False
        else:
            return True

########################################################################
class routes(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('routes')
    __tablename__ = 'routes'
    __table_args__ = {'autoload':True}


########################################################################
class nodetype(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('nodetype')
    __tablename__ = 'nodetype'
    __table_args__ = {'autoload':True} 

########################################################################
'''
class hosts(Base,mixin):
    """"""
    __tablename__ = 'hosts'
    __table_args__ = {'autoload':True}
'''
########################################################################
class noderes(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('noderes')
    __tablename__ = 'noderes'
    __table_args__ = {'autoload':True}

########################################################################
class switch(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('switch')
    __tablename__ = 'switch'
    __table_args__ = {'autoload':True}
########################################################################
class switches(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('switches')
    __tablename__ = 'switches'
    __table_args__ = {'autoload':True}
########################################################################
class mac(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('mac')
    __tablename__ = 'mac'
    __table_args__ = {'autoload':True}
########################################################################
class hwinv(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('hwinv')
    __tablename__ = 'hwinv'
    __table_args__ = {'autoload':True}
########################################################################
class postscripts(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('postscripts')
    __tablename__ = 'postscripts'
    __table_args__ = {'autoload':True}
    
########################################################################
class bootparams(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('bootparams')
    __tablename__ = 'bootparams'
    __table_args__ = {'autoload':True}

########################################################################
class nodelist(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('nodelist')
    __tablename__ = 'nodelist'
    __table_args__ = {'autoload':True}

########################################################################
class vm(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('vm')
    __tablename__ = 'vm'
    __table_args__ = {'autoload':True}
########################################################################
class nodehm(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('nodehm')
    __tablename__ = 'nodehm'
    __table_args__ = {'autoload':True}
########################################################################
class nodegroup(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('nodegroup')
    __tablename__ = 'nodegroup'
    __table_args__ = {'autoload':True}
########################################################################
class vpd(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('vpd')
    __tablename__ = 'vpd'
    __table_args__ = {'autoload':True}
########################################################################
class servicenode(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('servicenode')
    __tablename__ = 'servicenode'
    __table_args__ = {'autoload':True}
########################################################################
class hosts(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('hosts')
    __tablename__ = 'hosts'
    __table_args__ = {'autoload':True}
########################################################################
class nics(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('nics')
    __tablename__ = 'nics'
    __table_args__ = {'autoload':True}
########################################################################
class osimage(Base,mixin):
    """"""
    Base.metadata.bind = getEngine('osimage')
    __tablename__ = 'osimage'
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

    session = loadSession('hosts')
    print "======hosts======================"
    x = session.query(hosts).all()
    for item in x:
        print item.ip,item.hostnames

    session = loadSession('passwd')
    print "======passwd======================"
    x = session.query(passwd).all()
    for item in x:
        print item.key,item.username

    print "======routes======================"
    x = session.query(routes).all()
    for item in x:
        print item.net,item.mask
    print "======networks======================"
    session = loadSession('networks')
    nodelist_value = {}
    nodelist = ['node0001','node0002']
    mymac={}
    mymac['node0001']={}
    mymac['node0001']['node']="node0001"
    mymac['node0001']['mac']="11:22:33:44"
    print networks.getkey()
    exit()

    print dir(mac.getkey())
    print mac.getkey().asc
    mynode=mac(mymac['node0001'])
    print mynode.getdict()
    #mymac=mac()
    #session.add(mymac)
    #session.commit()
    print dir(mac)
    session.close()
