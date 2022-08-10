import configparser

class DeathnoteConfig:
	
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config/config.ini')
	
	def get_config(self, section, param):
		return self.config[section][param]

	def set_config(self, section, param, value):
		self.config[section][param] = value
