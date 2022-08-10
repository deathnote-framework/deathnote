from core.storage import LocalStorage
from base.exceptions import OptionValidationError
from core.utils.function import *
import os
import importlib

class Option:
	
	def __init__(self, default, description="", required="no", advanced=False):
		
		self.description = description
		self.required = required
		
		if default:
			self.__set__("", default)
		else:
			self.display_value = ""
			self.value = ""

		self.advanced = bool(advanced)

	def __get__(self, instance, owner):
		return self.value

class OptString(Option):
	""" Option String attribute """

	def __set__(self, instance, value):
		try:
			self.value = self.display_value = str(value)
		except ValueError:
			raise OptionValidationError("Invalid option. Cannot cast '{}' to string.".format(value))

class OptPort(Option):
	""" Option Port attribute """

	def __set__(self, instance, value):
		try:
			value = int(value)

			if 0 < value <= 65535:  # max port number is 65535
				self.display_value = str(value)
				self.value = value
			else:
				raise OptionValidationError("Invalid option. Port value should be between 0 and 65536.")
		except ValueError:
			raise OptionValidationError("Invalid option. Cannot cast '{}' to integer.".format(value))
				
class OptInteger(Option):
	""" Option Integer attribute """

	def __set__(self, instance, value):
		try:
			self.display_value = str(value)
			self.value = int(value)
		except ValueError:
			raise OptionValidationError("Invalid option. Cannot cast '{}' to integer.".format(value))

class OptSession(Option):
	""" Option Session attribute """
	
	def __set__(self, instance, value):
		try:
			value = int(value)
			local_storage = LocalStorage()
			session_active = local_storage.get("sessions")
			if value in session_active.keys():
				self.display_value = str(value)
				self.value = int(value)
			else:
				raise OptionValidationError("Invalid option. Session don't exist")
		except ValueError:
			raise OptionValidationError("Invalid option. Cannot cast '{}' to integer.".format(value))

class OptBool(Option):
	""" Option Bool attribute """

	def __init__(self, default, description="", required="no", advanced=False):
		self.description = description
		self.required = required

		if default:
			self.display_value = "true"
		else:
			self.display_value = "false"

		self.value = default

		try:
			self.advanced = bool(advanced)
		except ValueError:
			raise OptionValidationError("Invalid value. Cannot cast '{}' to boolean.".format(advanced))

class OptPayload(Option):
	""" Option Payload attribute """

	def __set__(self, instance, value):
		payload = instance._add_payload_option(value)
		try:
			self.value = self.display_value = str(value)
		except ValueError:
			raise OptionValidationError("Invalid option. Cannot cast '{}' to string.".format(value))

	def __get__(self, instance, owner):
		payload_path = pythonize_path(self.display_value)
		module_payload = ".".join(("modules",payload_path))
		module_payload = getattr(importlib.import_module(module_payload), "Module")()
		_payload = module_payload.generate()
		if "encoder" in owner.exploit_attributes:
			if owner.exploit_attributes["encoder"][0]:
				encoder_path = pythonize_path(owner.exploit_attributes["encoder"][0])
				module_encoder = ".".join(("modules",encoder_path))
				module_encoder = getattr(importlib.import_module(module_encoder), "Module")()
				_payload = module_encoder.encode(_payload)		
		return _payload
	
class OptIP(Option):
	""" Option IP attribute """

	def __set__(self, instance, value):
		if not value or is_ipv4(value) or is_ipv6(value):
			self.value = self.display_value = value
		else:
			raise OptionValidationError("Invalid address. Provided address is not valid IPv4 or IPv6 address.")

class OptFile(Option):
	""" Option file attribute """
	
	def __get__(self, instance, owner):

		path = self.display_value
		if path.startswith("file://"):
			path = path.replace("file://", "")
			path = os.getcwd()+"/data/"+path
			if not os.path.exists(path):
				raise OptionValidationError("File '{}' does not exist.".format(path))
		with open(path, "r") as f:
			content = f.readlines()
			return content

	def __set__(self, instance, value):

		self.value = self.display_value = value	
