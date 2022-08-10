available_platform = ['linux', 
						'unix', 
						'windows', 
						'osx', 
						'android']

available_arch = ['x86',
					'x64',
					'arm',
					'arm64']

class Metadata:
    
	def __init__(self, module):
		self.module = module

	def check_name(self):
		if self.module.__info__['name']:
			if isinstance(self.module.__info__['name'], str):
				return True
		return False

	def check_description(self):
		if self.module.__info__['description']:
			if isinstance(self.module.__info__['description'], str):
				return True
		return False

	def check_cve(self):
		if self.module.__info__['cve']:
			if isinstance(self.module.__info__['cve'], list):
				return True
		return False

	def check_platform(self):
		if self.module.__info__['platform']:
			if isinstance(self.module.__info__['platform'], list):
				for i in self.module.__info__['platform']:
					if i in available_platform:
						return True
		return False
