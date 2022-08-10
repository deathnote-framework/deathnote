from core.base.base_module import BaseModule 
from core.utils.printer import *

class File(BaseModule):

	def command_exists(self, cmd):
		""" Check if a command exists on the current system """
		if self.current_session('platform') == 'windows':
			if 'true' in self.cmd_exec(f"cmd /c where /q {cmd} & if not errorlevel 1 echo true"):
				return True
		else:
			if 'true' in self.cmd_exec(f"command -v {cmd} && echo true"):
				return True
	
	def read_file(self, filename):
		""" Read a file and return its content """
		if self.current_session('platform') == 'windows':
			return self.cmd_exec(f'type {filename}')
		
		elif self.command_exists('cat'):
			return self.cmd_exec(f'cat {filename}')
		
		return False		

	def write_file(self, data, filename):
		""" Write data to a file """
		if self.current_session['platform'] == 'windows':
			self.cmd_exec(f'echo | set /p "{data}" > "{filename}"')
		else:
			self.cmd_exec(f"printf '{data}' > {filename}")

	def upload_file(self, remotefile, localfile):
#		""" Upload a file to the target """
#		if self.current_session['platform'] == 'windows':
#			self.cmd_exec(f"cmd.exe /C copy \"{localfile}\" \"{remotefile}\"")
#		else:
#			self.cmd_exec(f"cp {localfile} {remotefile}")
		
		pass

	def chmod_x(self, filename):
		""" Set file to executable """
		if self.current_session['platform'] == 'windows':
			self.cmd_exec(f"cmd.exe /C attrib +x \"{filename}\"")
		else:
			self.cmd_exec(f"chmod +x {filename}")
	
	def file_exist(self, filename):
		""" Check if a file exists """
		if self.current_session['platform'] == 'windows':
			response = self.cmd_exec(f"cmd.exe /C IF exist \"{filename}\" ( echo true )")
			if response == "true":
				return True
			return False
		else:
			response = self.cmd_exec(f"test -f \"{filename}\" && echo true")
			if response == "true":
				return True
			return False
	
	def pwd(self):
		""" Print current working directory """
		if self.current_session['platform'] == 'windows':
			return self.cmd_exec('cd')
		else:
			return self.cmd_exec('pwd')
	
	def directory(self):
		""" List files in the current directory """
		if self.current_session['platform'] == 'windows':
			return self.cmd_exec('dir')
		else:
			return self.cmd_exec('ls')

	def file_rm(self, filename):
		if self.current_session['platform'] == 'windows':
			return self.cmd_exec('rd /s /q "{filename}"')
		else:
			return self.cmd_exec(f'rm -f "{filename}"')