from pkg_resources import parse_version

class LocalScan:

	def __init__(self, session=0):
		self.session = session
	
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
			lib_loaded = __import__('core.base.lib_localscan.{}'.format(data), fromlist=[func])
			return getattr(lib_loaded, func)(self.session)
		except ModuleNotFoundError as e:
			return
		except Exception as e:
			return

	def version_compare(self, version):
		return parse_version(version)