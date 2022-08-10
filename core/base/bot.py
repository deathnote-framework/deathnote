from core.base.base_module import BaseModule
from core.utils.function import *
import importlib

class Bot(BaseModule):

	def __init__(self):
		super(Bot, self).__init__()
		self.type_module = "bot"
		self.listener = None

	def run(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def exploit(self):
		# load listener
		listener = self._Module__info__['listener']
		listener = pythonize_path(listener)
		self.listener = getattr(importlib.import_module("modules."+listener), "Module")()
		self.run()
		self.listener.exploit()
		
	def on_connect(self):
		raise NotImplementedError()
	
	def add_option(self, option, value):
		setattr(self.listener, option, value)
		self.listener.exploit_attributes[option][0] = value
