import importlib
from base.exceptions import DeathnoteException

def import_exploit(path: str):
	""" Imports exploit module

	:param str path: absolute path to exploit e.g. deathnote.modules.exploits.asus_auth_bypass
	:return: exploit module or error
	"""

	try:
		module = importlib.import_module(path)
		if hasattr(module, "Module"):
			return getattr(module, "Module")
		else:
			raise ImportError("No module named '{}'".format(path))

	except (ImportError, AttributeError, KeyError) as err:
		raise DeathnoteException(
			"Error during loading '{}'\n\n"
			"Error: {}\n\n"
			"It should be valid path to the module. "
			"Use <tab> key multiple times for completion.".format(path, err)
		)

def reload_module(path: str):
	try:
		module = importlib.reload(path)
		if hasattr(module, "Module"):
			return getattr(module, "Module")
		else:
			raise ImportError("No module named '{}'".format(path))		
	except:
		pass
