from deathnote_module import *
import socket

class Module(Listener):
	__info__ = {
		"name": "Listen shell tcp",
		"type": "reverse",
		"session": "shell",
		"description": "Connect back to attacker and spawn a command shell",
	}
	
	lhost = OptString("127.0.0.1", "Target IPv4 or IPv6 address", "yes")
	lport = OptPort(4444, "Target HTTP port", "no")

	def run(self):
		try:
			print_status(f"Start server on {self.lhost}:{self.lport}")
			print_status("Waiting connection...") 
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.bind((self.lhost, self.lport))
			self.sock.listen(5)
			client, address = self.sock.accept()
			return (client, address)
		except KeyboardInterrupt:
			return False
		except OSError as e:
			print_error(e)
			return False

	def close(self, sock):
		sock.close()
