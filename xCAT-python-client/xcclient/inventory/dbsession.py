from sqlalchemy import create_engine,inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine=create_engine('postgresql+psycopg2://xcatadm:cluster@localhost/xcatdb',echo=False)
Base = declarative_base(engine)

def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
