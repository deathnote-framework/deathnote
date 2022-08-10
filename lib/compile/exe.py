from core.base.base_module import BaseModule 
from base.format.elf import ELF
from base.format.pe import PE
from core.utils.printer import *

class Exe(BaseModule):
	
	def generate_payload_elf(self, arch, payload):
		""" Generate an ELF payload """

		if arch in ['x64', 'x86', 'aarch64', 'mipsle', 'mipsbe', 'armle']:
			elf = ELF()
			content = elf.generate(arch, payload)
			return content
		print_error("Arch not valid for generate payload")
		return False
	
	def generate_payload_exe(self, arch, payload):
		""" Generate an EXE payload """
		if arch in ['x64', 'x86']:
			pe = PE()
			content = pe.generate(arch, payload)
			return content 
		print_error("Arch not valid for generate payload")
		return False

	def generate_payload_dll(self, arch, payload):
		""" Generate a DLL payload """
		pass

	def generate_payload_jar(self, payload):
		""" Generate a JAR payload """
		pass
	
	def generate_payload_war(self, payload):
		""" Generate a WAR payload """
		pass

	def generate_payload(self, arch, payload, platform="unix"):
		if platform == "unix":
			return self.generate_payload_elf(arch, payload)
		elif platform == "linux":
			return self.generate_payload_elf(arch, payload)
		elif platform == "windows":
			return self.generate_payload_exe(arch, payload)
		else:
			return False