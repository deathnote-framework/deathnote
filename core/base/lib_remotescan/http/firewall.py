import re
from deathnote.core.base.remote_scan_lib.http.http_func import Http_func

class Firewall(Http_func):
				
	def check(self):
		return self.http_get(self.target)

