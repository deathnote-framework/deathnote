from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base
import datetime
import warnings
import os
from sqlalchemy import exc as sa_exc

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)

Base = declarative_base()

class Modules(Base):
	
	__tablename__ = 'modules'

	id = Column(Integer, primary_key=True, autoincrement=True)
	type_module = Column(Text)
	path = Column(Text)
	name = Column(Text)
	description = Column(Text)
	cve = Column(Text)
	plugin = Column(Text)
	platform = Column(Text)
	arch = Column(Text)

	def __init__(self, type_module="", path="", name="", description="", cve="", plugin="", platform="", arch=""):
		self.type_module = type_module
		self.path = path
		self.name = name
		self.description = description
		self.cve = cve
		self.plugin = plugin
		self.platform = platform
		self.arch = arch

class Meta(Base):
	
	__tablename__ = 'meta'
	
	name = Column(Text, primary_key=True)
	value = Column(Text)

	def __init__(self, name="nvd",value=""):
		self.name = name
		self.value = value

class Cve(Base):
	
	__tablename__ = 'cve'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	cve_id = Column(Text)
	summary = Column(Text)
	vendors = Column(Text)
	cwes = Column(Text)
	cvss2 = Column(Text)
	cvss3 = Column(Text)
	create_at = Column(DateTime)
	update_at = Column(DateTime)

	def __init__(self, cve_id="", summary="",vendors="",cwes="",cvss2="",cvss3="",create_at= datetime.datetime.utcnow,update_at=datetime.datetime.utcnow):
		self.cve_id=cve_id
		self.summary=summary
		self.vendors=vendors
		self.cwes=cwes
		self.cvss2=cvss2
		self.cvss3=cvss3
		self.create_at=create_at
		self.update_at=update_at

class Workspace_data(Base):
	
	__tablename__ = 'workspace_data'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Text) # nom du workspace
	target = Column(Boolean) # true si c est une target false si c est un port
	ip = Column(Text)
	port = Column(Integer)
	
	def __init__(self, name="", target=False, ip="", port=0):
		self.name = name
		self.target = target
		self.ip = ip
		self.port = port

class Workspace(Base):
	
	__tablename__ = 'workspace'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Text)	
	
	def __init__(self, name=""):
		self.name = name

class Remotescan(Base):
	
	__tablename__ = 'remotescan'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	workspace = Column(Text)
	target = Column(Text)
	status = Column(Text)
	
	def __init__(self, workspace="default", target="", status=""):
		self.workspace=workspace
		self.target=target
		self.status=status

class Remotescan_data(Base):
	
	__tablename__ = 'remotescan_data'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	remotescan_id = Column(Text)
	target = Column(Text)
	port = Column(Integer)
	cvss3 = Column(Text)
	nom = Column(Text)
	cve = Column(Text)
	modules = Column(Text)
	info = Column(Text)
	
	def __init__(self, remotescan_id=0, target="", port=0, cvss3="", nom="", cve="", modules="", info=""):
		self.remotescan_id = remotescan_id
		self.target = target
		self.port = port
		self.cvss3 = cvss3
		self.nom = nom
		self.cve = cve
		self.modules = modules
		self.info = info

class Localscan(Base):
	
	__tablename__ = 'localscan'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	workspace = Column(Text)
	target = Column(Text)
	status = Column(Text)
	
	def __init__(self, workspace="default", target="", status=""):
		self.workspace = workspace
		self.target=target
		self.status=status

class Localscan_data(Base):
	
	__tablename__ = 'localscan_data'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	localscan_id = Column(Text)
	target = Column(Text)
	cvss3 = Column(Text)
	nom = Column(Text)
	cve = Column(Text)
	modules = Column(Text)
	info = Column(Text)
	
	def __init__(self, localscan_id=0, target="", cvss3="", nom="", cve="", modules="", info=""):
		self.localscan_id = localscan_id
		self.target = target
		self.cvss3 = cvss3
		self.nom = nom
		self.cve = cve
		self.modules = modules
		self.info = info		

class Credentials(Base):
	
	__tablename__ = 'credentials'
	
	id = Column(Integer, primary_key=True, autoincrement=True)
	module_name = Column(Text)
	host = Column(Text)
	username = Column(Text)
	password = Column(Text)
	data = Column(Text)
	
	def __init__(self, module_name="", host="", username="", password="", data=""):
		self.module_name = module_name
		self.host = host
		self.username = username
		self.password = password
		self.data = data

if not os.path.exists("db"):
    os.mkdir("db")

engine = create_engine('sqlite:///db/deathnote.db?check_same_thread=False', echo=False)
Db_session = sessionmaker(bind=engine)
Session = scoped_session(Db_session)
db = Session()

def create_db():
	Base.metadata.create_all(engine)


