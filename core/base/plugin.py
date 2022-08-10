from core.utils.import_module import import_exploit
from core.utils.function import *

class Plugin:
	
	def __init__(self):
		self.type_module = "plugin"	
	
	def run(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def load_module(self, module):
		try:
			my_module = import_exploit("modules."+pythonize_path(module))()
			return my_module
		except SyntaxError as e:
			print_error(e)
		except AttributeError as e:
			print_error(e)
		except NameError as e:
			print_error(e)
		except KeyboardInterrupt as e:
			print_error(e)
		except ValueError as e:
			print_error(e)
		return

	def add_option(self, module, name, value):
		setattr(module, name, value)
  
	def run_module(self, module):
		module.exploit()

	def output_module(self, module):
		return module._output