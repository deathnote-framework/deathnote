from core.base.base_module import BaseModule
from core.base.option import *
import socket

class TCPSocket:

	def __init__(self, lhost, lport, timeout=10):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.lhost = lhost
		self.lport = lport
		self.sock.settimeout(timeout)

	def settimeout(self, timeout=10):
		self.sock.timeout = timeout

	def listen(self):
		self.sock.bind((self.lhost, int(self.lport)))
		self.sock.listen(5)
		client, address = self.sock.accept()
		return (client, address)	
	
	def send(self,data):
		self.sock.send(data.encode())
		
	def recv(self):
		data = self.sock.recv(1024)
		return data.decode()

	def close(self):
		self.sock.close()

class Tcp_server(BaseModule):

	target = OptString("127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", "yes")
	port = OptPort(80, "Target TCP port", "yes")

	def open_tcp(self, host, port, timeout=10):
		return TCPSocket(host, port, timeout)
