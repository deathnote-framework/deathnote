import re
from core.base.lib_localscan.func import Func

class Browser(Func):
	
	def get_browser(self):
		""" Get browser """
		
		if 'Chrome' in self.platform:
			return 'chrome'
		elif 'Firefox' in self.platform:
			return 'firefox'
		return False
	
	def get_version_browser(self):
		""" Get version of browser """
		
		if self.version:
			return self.version			
		return False	

	def get_version_os(self):
		""" Get version of os """
		
		if 'Android' in self.os:
			return 'android'
		elif 'Linux' in self.os:
			return 'linux'
		elif 'Windows' in self.os:
			return 'windows'
		else:
			pass
		 
