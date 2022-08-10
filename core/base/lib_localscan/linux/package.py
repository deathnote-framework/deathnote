from core.base.lib_localscan.func import Func

class Package(Func):
		

	def get_release(self):
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
		package = self.send(f'dpkg -s {pkg}')
		if package.startswith(f"Package: {pkg}"):
			return True
		return False
	
	def get_package_version(self, pkg):
		package = self.send(f'dpkg -s {pkg}').split('\n')
		for i in package:
			if i.startswith('Version:'):
				version = i.partition(':')[2].strip()
				return version
