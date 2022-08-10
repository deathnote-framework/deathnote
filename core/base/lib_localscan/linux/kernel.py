from core.base.lib_localscan.func import Func

class Kernel(Func):
		
	def version(self):
		""" Get kernel version """
		version = self.send("uname -r")
		return version

	def get_release(self):
		""" Get kernel release """

		release = self.send("lsb_release -a").split('\n')
		for i in release:
			if i.startswith("Distributor ID:"):
				distributor = i.split(':')[1].strip()
				distributor = distributor.upper()
			if i.startswith("Release:"):
				release = i.split(':')[1].strip()
				release.upper()
		return distributor+release

	def get_package(self, pkg):
		""" Get package exists """		
		package = self.send(f'dpkg -s {pkg}')
		if package.startswith("Package:"):
			return True
		return False
	
	def get_package_version(self, pkg):
		""" Get package version """
		package = self.send(f'dpkg -s {pkg}').split('\n')
		for i in package:
			if i.startswith('Version:'):
				version = i.split(':')[1].strip()
				return version
