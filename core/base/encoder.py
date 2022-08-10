from core.base.base_module import BaseModule
from core.utils.printer import *
from core.base.option import *

class Encoder(BaseModule):

	def __init__(self):
		super(Encoder, self).__init__()
		self.type_module = "encoder"

	def run(self):
		print_error("Module encoder cannot be run")	

	def exploit(self):
		self.run()

	def encode(self):
		raise NotImplementedError("Please implement 'encode()' method")
