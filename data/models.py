# This script is a start to adding a nice python object interface to our bikeshare data in PostgreSQL.
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from EnumSymbol import DeclEnum

from hello import engine, session

engine = create_engine("postgresql://"+print os.environ.get('dbuser')+'@'print os.environ.get('dburl')+'/'+print os.environ.get('dbname'))

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Base = declarative_base()

class Snapshot(base):
	tfl_id
	bikes
	spaces
	timestamp

class NewYork(Snapshot):
	__table__ = 'bike_ind_newyork'
	tfl_id = Column('tfl_id',Integer, primary_key=True)
	bikes = Column('bikes',Integer)
	spaces = Column('spaces',Integer)
	total_docks = Column('total_docks',Integer)
	timestamp = Column('timestamp',Timestamp)

class Chicago(Snapshot):
	__table__ = 'bike_ind_chicago'
	tfl_id = Column('tfl_id',Integer, primary_key=True)
	bikes = Column('bikes',Integer)
	spaces = Column('spaces',Integer)
	total_docks = Column('total_docks',Integer)
	timestamp = Column('timestamp',Timestamp)

class Boston(Snapshot):
	__table__ = 'bike_ind_boston'
	tfl_id = Column('tfl_id',Integer, primary_key=True)
	bikes = Column('bikes',Integer)
	spaces = Column('spaces',Integer)
	timestamp = Column('timestamp',Timestamp)

class WashingtonDC(Snapshot):
	__table__ = 'bike_ind_washingtondc'
	tfl_id = Column('tfl_id',Integer, primary_key=True)
	bikes = Column('bikes',Integer)
	spaces = Column('spaces',Integer)
	timestamp = Column('timestamp',Timestamp)

class Minneapolis(Snapshot):
	__table__ = 'bike_ind_minneapolis'
	tfl_id = Column('tfl_id',Integer, primary_key=True)
	bikes = Column('bikes',Integer)
	spaces = Column('spaces',Integer)
	timestamp = Column('timestamp',Timestamp)


		

		

