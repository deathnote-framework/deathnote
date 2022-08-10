from capstone import *
from keystone import *
from binascii import unhexlify

class Analyse_code:

	def __init__(self, platform="linux", arch="x32"):
		self.archs = ['x16','x32','x64','arm_32','arm_64','mips_32','mips_64']
		self.platform_list = ['linux','windows']
		self.platform = platform
		self.arch = arch
		

		try:
			self.archs_list = (
				{ # Keystone - Assembler
					'x16':     (KS_ARCH_X86,     KS_MODE_16),
					'x32':     (KS_ARCH_X86,     KS_MODE_32),
					'x64':     (KS_ARCH_X86,     KS_MODE_64),
					'arm':     (KS_ARCH_ARM,     KS_MODE_ARM),
					'arm_t':   (KS_ARCH_ARM,     KS_MODE_THUMB),
					'arm64':   (KS_ARCH_ARM64,   KS_MODE_LITTLE_ENDIAN),
					'mips32':  (KS_ARCH_MIPS,    KS_MODE_MIPS32),
					'mips64':  (KS_ARCH_MIPS,    KS_MODE_MIPS64)
				},
				{ # Capstone - Disassembler
					'x16':     (CS_ARCH_X86,     CS_MODE_16),
					'x32':     (CS_ARCH_X86,     CS_MODE_32),
					'x64':     (CS_ARCH_X86,     CS_MODE_64),
					'arm':     (CS_ARCH_ARM,     CS_MODE_ARM),
					'arm_t':   (CS_ARCH_ARM,     CS_MODE_THUMB),
					'arm64':   (CS_ARCH_ARM64,   CS_MODE_LITTLE_ENDIAN),
					'mips32':  (CS_ARCH_MIPS,    CS_MODE_MIPS32),
					'mips64':  (CS_ARCH_MIPS,    CS_MODE_MIPS64),
				}
			)
		except:
			self.archhs = ({})

	def setarch(self, new_arch):
		""" Sets the architecture """
		if new_arch in self.archs:
			self.arch = new_arch
			return True
		return False

	def setplatform(self, platform):
		""" Sets the platform """
		if platform in self.platform_list:
			self.platform = platform
			return True
		return False

	def assembly(self, code):
		""" Assembles code and returns a dictionary with the following keys:"""
		try:
			ks = Ks(self.archs_list[0][self.arch][0],self.archs_list[0][self.arch][1])
			asm = ks.asm(code)
			asm = ["\\x%.2x" % x for x in asm[0]]
			raw = "".join(asm)
			hex_string = raw.replace("\\x", "")
			output = {'Bytes count': str(len(asm)), 'Raw bytes': raw, 'Hex string': hex_string}
			return output
		except:
			return False

	def asm(self, code, arch=""):
		""" Assembles code """
		if arch == "":
			arch = self.arch
		else:
			if arch not in ['x16','x32','x64','arm_32','arm_64','mips_32','mips_64']:
				
				return False
		try:
			ks = Ks(self.archs_list[0][arch][0], self.archs_list[0][arch][1])
			machine = ks.asm(code.encode())
			if machine:
				return bytes(machine[0])
			return b''
		except:
			return False

	def disassembly(self, code):
		""" Disassembles code and returns a dictionary with the following keys:"""
		try:
			cs = Cs(self.archs_list[1][self.arch][0],self.archs_list[1][self.arch][1])
			output = []
			for i in cs.disasm(unhexlify(self.cleanup(code)), 0x1000):
				address = f"0x{i.address}"
				output.append({'address': address, 'mnemonic': i.mnemonic, 'op_str': i.op_str})
			return output
		except:
			return False

	def cleanup(self, input_str):
		""" Cleans up the input string """
		input_str = input_str.replace(" ", "")
		input_str = input_str.replace("\\x", "")
		return input_str.replace("0x", "")
