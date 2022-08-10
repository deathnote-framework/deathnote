from core.base.option import Option, OptString, OptPort, OptInteger, OptPayload
from future.utils import with_metaclass, iteritems
from base.analyse import Analyse_code
from core.utils.printer import *
from itertools import chain, cycle
import random
import string
import os
import struct
import shutil
import base64

class ModuleOptionsAggregator(type):

	def __new__(cls, name, bases, attrs):
		try:
			base_exploit_attributes = chain([base.exploit_attributes for base in bases])
		except AttributeError:
			attrs["exploit_attributes"] = {}
		else:
			attrs["exploit_attributes"] = {k: v for d in base_exploit_attributes for k, v in iteritems(d)}
		for key, value in list(iteritems(attrs)):
			if isinstance(value, Option):
				value.label = key
				attrs["exploit_attributes"].update({key: [value.display_value, value.required, value.description, value.advanced]})
			elif key == "__info__":
				attrs["_{}{}".format(name, key)] = value
				del attrs[key]
			elif key in attrs["exploit_attributes"]:
				del attrs["exploit_attributes"][key]

		return super(ModuleOptionsAggregator, cls).__new__(cls, name, bases, attrs)

class BaseModule(with_metaclass(ModuleOptionsAggregator,object)):

	def __init__(self):
		self._exploit_failed = False
		self._output = []

	def __str__(self):
		return self.__module__.split('.', 2).pop().replace('.', os.sep)

	@property
	def options(self):
		return list(self.exploit_attributes.keys())
	
	def asm(self, code, arch=""):
		assembly = Analyse_code()
		c = assembly.asm(code, arch)
		return c

	def convert_ip(self, address: str) -> bytes:

		ip = b""
		for i in address.split("."):
			ip += bytes([int(i)])
		return ip

	def convert_port(self, port: int) -> bytes:

		p = "%.4x" % int(port)
		return bytes.fromhex(p)

	def vulnerable(self):
		print_success('The target is vulnerable!')

	def not_vulnerable(self):
		print_error('The target is not vulnerable')
		self._exploit_failed = True

	def random_number(self,length:int, number: str = string.digits):
		return int("".join(random.choice(number) for _ in range(length)))	

	def random_text(self, length: int, alph: str = string.ascii_letters):
		return "".join(random.choice(alph) for _ in range(length))

	def xor(self, x, y):
		return bytes(a ^ b for a, b in zip(b(x), b(y)))	

	def xor_key_bytes(self, buffer: bytes, key: bytes):
		return bytes([a ^ b for a, b in zip(buffer, cycle(key))])
	
	def write_dir(self, filename, data):
		if not os.path.exists("output"):
			os.mkdir("output")
		with open(f"output/{filename}", "a") as f:
			f.write(data)
			f.close()
			print_success(f"File successfully created: output/{filename}")
			return True
		return False

	def create_out_dir(self, directory):
		if not os.path.exists("output"):
    			os.mkdir("output")     
		try:
			shutil.rmtree(os.getcwd()+"/output/"+directory)
		except:
			pass
		os.mkdir(os.getcwd()+"/output/"+directory)
	
	def rm_dir(self, filename):
		try:
			shutil.rmtree(os.getcwd()+"/output/"+filename)
		except:
			pass
		
	def p32(self, n):
		return struct.pack('<I', n)

	def p64(self, n):
		return struct.pack('<Q', n)

	def u32(self, x):
		return struct.unpack('<I', b(x))[0]

	def u64(self, x):
		return struct.unpack('<Q', b(x))[0]		
	
	def encode_base64(self, data):
		if isinstance(data, bytes):
			return base64.b64encode(data)
		else:
			return base64.b64encode(data.encode())			
	
	def decode_base64(self, data):
		if isinstance(data, bytes):
			return base64.b64decode(data)
		else:
			return base64.b64decode(data.encode())
