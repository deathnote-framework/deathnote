from core.base.base_module import BaseModule
from core.utils.printer import *
from core.base.option import *
from core.utils.function import *
import importlib
from socket import inet_aton

class Payload(BaseModule):

	type_module = "payload"

	def __init__(self):
		super(Payload, self).__init__()

	def generate(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def exploit(self):
		if self.encoder:
			try:
				_payload = self.generate()
				encoder_path = pythonize_path(self.encoder)
				module_encoder = ".".join(("modules", encoder_path))
				module_encoder = getattr(importlib.import_module(module_encoder), "Module")()
				_encoder = module_encoder.encode(_payload)
				return _encoder
			except Exception as e:
				print(e)
				return None
			except:
				print_error("Problem with encoder")
		return self.generate()

	def shellcode_ip(self, ip_address):
		ip = inet_aton(ip_address)
		return ip
	
	def shellcode_port(self, port_number):
		port = inet_aton(str(port_number))
		return port[2:]
