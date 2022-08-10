import sys
import os
major, minor, micro, release_level, serial = sys.version_info
if major < 3 and minor < 6:
	print("[!] Deathnote requires Python 3.6 or higher.")
	sys.exit(1)

from base.create_config import create_config_file
if not os.path.isfile('config/config.ini'):
	create_config_file()
from core.console import Interpreter
from core.storage import LocalStorage
from core.utils.module_parser import *
from core.utils.db import db, Workspace, create_db

def main():
	""" Deathnote framework. """
	local_storage = LocalStorage()
	local_storage.set("workspace", "default")
	framework = Interpreter()
	framework.start()  
	
if __name__ == "__main__":
	try:		
		if not os.path.isfile('db/deathnote.db'):
			print("Database initialisation")
			create_db()
			default = Workspace("default")
			db.add(default)
			db.commit()
		main()
	except (KeyboardInterrupt, SystemExit):
		sys.exit(0)    
