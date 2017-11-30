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


dbcfgpath='/etc/xcat/cfgloc'
dbcfgregex=re.compile("^(\S+):dbname=(\S+);host=(\S+)\|(\S+)\|(\S*)$")

engine_value = 'sqlite:///:/etc/xcat'
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
         

engine=create_engine(engine_value,echo=False)
Base = declarative_base(engine)

def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

