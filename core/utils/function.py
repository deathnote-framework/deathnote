from core.utils.db import *
from core.utils.printer import *
from sqlalchemy import or_


def parse_command_line(line):
	kwargs = dict()
	command, _, arg = line.strip().partition(" ")
	return command, arg.strip(), kwargs

def index_modules():
	""" Returns list of all exploits modules

	:param str modules_directory: path to modules directory
	:return list: list of found modules
	"""
	
	modules_query = db.query(Modules.path).filter(or_(Modules.type_module=='exploits', 
											Modules.type_module=='auxiliary',
											Modules.type_module=='post',
											Modules.type_module=='browser_exploits',
											Modules.type_module=='browser_auxiliary',
											Modules.type_module=='backdoors',
											Modules.type_module=='listeners',
											Modules.type_module=='payloads',
											Modules.type_module=='dev')).all()
	modules = [value for value, in modules_query]
	return modules

def pythonize_path(path):
	""" Replaces argument to valid python dotted notation.

	ex. foo/bar/baz -> foo.bar.baz

	:param str path: path to pythonize
	:return str: pythonized path
	"""

	return path.replace("/", ".")


def humanize_path(path):
	""" Replace python dotted path to directory-like one.

	ex. foo.bar.baz -> foo/bar/baz

	:param str path: path to humanize
	:return str: humanized path
	"""

	return path.replace(".", "/")
