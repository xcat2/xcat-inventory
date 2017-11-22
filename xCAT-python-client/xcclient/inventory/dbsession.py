from sqlalchemy import create_engine,inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

if os.path.exists('/etc/xcat/cfgloc'):
    db_info = open('/etc/xcat/cfgloc')
else:
    engine_value = 'sqlite:///:/etc/xcat'
try:
     all_the_text = db_info.read( )
     db_line = all_the_text.strip()
     db_type = db_line.split(':')[0]
     if db_type == 'Pg':
         conn="postgresql+psycopg2://"
     elif db_type == 'mysql':
         conn="mysql+pymysql://"
         
     dbname = db_line.split(';')[0].split('=')[-1]
     db_str = db_line.split(';')[-1].split('=')[-1].split('|')
     dbinfo = db_str[1]+":"+db_str[2]+"@"+db_str[0]+"/"+dbname
     engine_value = conn + dbinfo
     
finally:
     db_info.close( )

engine=create_engine(engine_value,echo=False)
Base = declarative_base(engine)

def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

