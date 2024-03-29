from core.base.base_module import BaseModule
from core.utils.printer import *

class Cisco(BaseModule):
	
	def cisco_ios_decrypt7(self, cipher):
		""" Decrypt Cisco IOS 7 passwords """
		
		result = ""
		cipher_hexa_list = list([int(cipher[i:i+2], 16) for i in range(0,len(cipher),2)])

		keys = [0x64, 0x73, 0x66, 0x64, 0x3b, 0x6b, 0x66, 
				0x6f, 0x41, 0x2c, 0x2e, 0x69, 0x79, 0x65, 
				0x77, 0x72, 0x6b, 0x6c, 0x64, 0x4a, 0x4b, 
				0x44, 0x64, 0x73, 0x66, 0x64, 0x3b, 0x6b, 
				0x66, 0x6f, 0x41, 0x2c, 0x2e, 0x69, 0x79,
				0x65, 0x77, 0x72, 0x6b, 0x6c, 0x64, 0x4a,
				0x4b, 0x44]

		n = int(cipher[0:2])

		for i in cipher_hexa_list[1:]:
			result += chr(i^keys[n])
			n+=1
		
		return result
