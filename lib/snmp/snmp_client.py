from core.base.base_module import BaseModule
from core.base.option import OptString, OptPort
from core.utils.printer import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

class Snmp_lib:

	def __init__(self, target, port):

		self.snmp_target = target
		self.snmp_port = port

	def get(self, community_string: str, oid: str, version: int = 1, retries: int = 0, timeout = 15.0, verbose=True):
		""" Get OID from SNMP server

		:param str community_string: SNMP server communit string
		:param str oid: SNMP server oid
		:param int version: SNMP protocol version
		:param int retries: number of retries
		:return bytes: SNMP server response
		"""

		cmdGen = cmdgen.CommandGenerator()

		try:
			errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
				cmdgen.CommunityData(community_string, mpModel=version),
				cmdgen.UdpTransportTarget((self.snmp_target, self.snmp_port), timeout=timeout, retries=retries),
				oid,
			)
		except Exception as err:
			print_error(self.peer, "SNMP Error while accessing server", err, verbose=verbose)
			return None

		if errorIndication or errorStatus:
			print_error(self.peer, "SNMP invalid community string: '{}'".format(community_string), verbose=verbose)
		else:
			print_success(self.peer, "SNMP valid community string found: '{}'".format(community_string), verbose=self.verbose)
			return varBinds

		return None

class Snmp_client(BaseModule):

	snmp_target = OptString("127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", "no")
	snmp_port = OptPort(165, "Target HTTP port", "no")
 
	def open_snmp(self, target=None, port=None):

		snmp_target = target if target else self.target
		snmp_port = port if port else self.port
	
		client = Snmp_lib(snmp_target, snmp_port)
		return client