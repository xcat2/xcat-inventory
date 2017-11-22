from dbsession import *
from copy import *
import pdb


########################################################################
class Password(Base):
    """"""
    __tablename__ = 'passwd'
    __table_args__ = {'autoload':True}

########################################################################
class Networks(Base):
    """"""
    __tablename__ = 'networks'
    __table_args__ = {'autoload':True}
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)


########################################################################
class Nodetype(Base):
    """"""
    __tablename__ = 'nodetype'
    __table_args__ = {'autoload':True} 
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)

########################################################################
class Hosts(Base):
    """"""
    __tablename__ = 'hosts'
    __table_args__ = {'autoload':True}
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)

########################################################################
class Noderes(Base):
    """"""
    __tablename__ = 'noderes'
    __table_args__ = {'autoload':True}
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)

########################################################################
class Switch(Base):
    """"""
    __tablename__ = 'switch'
    __table_args__ = {'autoload':True}
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)
########################################################################
class Mac(Base):
    """"""
    __tablename__ = 'mac'
    __table_args__ = {'autoload':True}
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)
########################################################################
class Postscripts(Base):
    """"""
    __tablename__ = 'postscripts'
    __table_args__ = {'autoload':True}
    
    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
            return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)
########################################################################
class Bootparams(Base):
    """"""
    __tablename__ = 'bootparams'
    __table_args__ = {'autoload':True}

    def __getattr__(self, key):
        if key == '_instance_dict' and key not in self.__dict__:
            self._sa_instance_state.initialize(key)
        return getattr(self, key)
        try:
            return self._instance_dict[key]
        except KeyError:
            return Base.__getattr__(self, key)


#----------------------------------------------------------------------

def query_table_by_node(session, tclass, tkey):
    """"""
    result=session.query(tclass).filter(tclass.node == tkey).all()
    return result


def query_nodelist_by_key(session, nodelist):
    """"""
    nodelist_value = {}
    for node in nodelist:
        nodeattr = {}
        classlist = [Bootparams,Nodetype,Hosts,Switch,Mac,Noderes]
        for eachclass in classlist:
            table_row = query_table_by_node(session,eachclass,node)
            tlist = eachclass.__table__.columns
            for t in tlist:
                v=t.name
                for item in table_row:
                    if item.__dict__[v]:
                         nodeattr[str(t)] = item.__dict__[v].encode()

        nodelist_value[node]=nodeattr
    return nodelist_value

if __name__ == "__main__":

    session = loadSession()
    nodelist_value = {}
    nodelist = ['bybc0607','node1']
    nodelist_value = query_nodelist_by_key(session,nodelist)
    print nodelist_value
    session.close()
