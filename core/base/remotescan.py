from core.utils.printer import *
from packaging import version

class RemoteScan:
	
	type_module = "remotescan"	
		
	def __init__(self,target="127.0.0.1", port=0, cache=None, ssl=False):
		self.target = target
		self.port = port
		self.cache = cache
		self.ssl = ssl

	def run(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def attack(self):
		try:
			return self.run()
		except:
			return False		

	def scan_lib(self,lib):
		try:
			data = lib.replace('/', '.')
			func = data.split('.')[-1:][0].capitalize()
			lib_loaded = __import__('core.base.lib_remotescan.{}'.format(data), fromlist=[func])
			return getattr(lib_loaded, func)(self.target, self.port, self.cache, self.ssl)
		except ModuleNotFoundError as e:
			return
		except Exception as e:
			return
