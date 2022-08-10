from core.base.base_module import BaseModule
from core.base.option import OptString
from core.utils.printer import *

class Http_login(BaseModule):
	
	username = OptString("admin", "A specific username to authenticate as", "yes")
	password = OptString("admin", "A specific password to authenticate with", "yes")

	
	def login_success(self):
		print_success('Login success')
	
	def login_failed(self):
		print_error('Login failed')
		try:
			self._exploit_failed = True
		except:
			pass
