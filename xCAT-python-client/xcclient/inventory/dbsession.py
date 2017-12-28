#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

from sqlalchemy import create_engine,inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import os
import sqlalchemy.exc

dbcfgpath='/etc/xcat/cfgloc'
dbcfgregex=re.compile("^(\S+):dbname=(\S+);host=(\S+)\|(\S+)\|(\S*)$")
Base = declarative_base()
Base.metadata.bind = None;

def createEngine(tablename=None):
    if os.path.exists(dbcfgpath):
        dbcfgfile = open(dbcfgpath)
        dbcfgloc = dbcfgfile.read( )
        dbcfgfile.close()
        try:
            (dbtype,dbname,dbhost,dbusername,dbpasswd)=re.findall(dbcfgregex,dbcfgloc)[0]
        except:
            print "Fatal: invalid cfgloc file "+dbcfgpath+"!"
            exit (1)
        if dbtype == 'Pg':
            conn="postgresql+psycopg2://"
        elif dbtype == 'mysql':
            conn="mysql+pymysql://"
        engine_value = conn+dbusername+':'+dbpasswd+'@'+dbhost+'/'+dbname
    elif tablename:
        engine_value = 'sqlite:////etc/xcat/'+tablename+'.sqlite'
    else:
        print "Fatal: empty table name"
        exit (1)
    engine=create_engine(engine_value,echo=False)
    return engine

def getEngine(tablename=None):
    """"""
    if os.path.exists(dbcfgpath):
        if not Base.metadata.bind:
            engine=createEngine()
        else:
            return Base.metadata.bind 
    elif tablename:
        engine=createEngine(tablename)
    return engine

def loadSession(tablename=None):
    """"""
    engine = getEngine(tablename)
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

