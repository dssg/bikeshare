from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from EnumSymbol import DeclEnum

from hello import engine, session

engine = create_engine("postgresql://postgres@ec2-54-218-252-167.us-west-2.compute.amazonaws.com/bikeshare")

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Base = declarative_base()

class Snapshot(base):


