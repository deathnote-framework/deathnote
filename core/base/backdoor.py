from core.base.base_module import BaseModule
from core.utils.printer import *
from core.base.option import *
from core.utils.function import *
import importlib

class Backdoor(BaseModule):

	listener = OptBool(False, "Start listener after generate backdoor", "no")
	name = OptString("backdoor", "name of your backdoor", "yes")

	def __init__(self):
		super(Backdoor, self).__init__()
		self.type_module = "backdoor"

	def run(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def exploit(self):
		print_status("Generating backdoor")
		self.run()
		try:
			print_success(f"Use listener : {self._Module__info__['handler']}")
			if self.listener:
				if self._Module__info__['handler']:
					prepare_handler = pythonize_path(self._Module__info__['handler'])
					handler = getattr(importlib.import_module("modules."+prepare_handler), "Module")()	
					for i in self.exploit_attributes.keys():
						if i in handler.exploit_attributes.keys():
							setattr(handler, i, self.exploit_attributes[i][0])
					handler.exploit()		
		except:
			print_error("Error with listener")