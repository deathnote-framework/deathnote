from core.base.base_module import BaseModule
from core.base.option import OptString, OptPort
from core.utils.printer import *
import socket

class TCPSocket:
	
	def __init__(self, host, port, timeout=10):
		self.host = host
		self.port = int(port)

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(timeout)

	def connect(self):
		try:
			self.sock.connect((self.host, self.port))
			return True
		except Exception:
			print_error("Failed to connect!")
		return False
	
	def settimeout(self, timeout):
		try:
			self.sock.settimeout(timeout)
			return True
		except Exception:
			print_error("Socket is not connected!")
		return False	

	def disconnect(self):
		try:
			self.sock.close()
			return True
		except Exception:
			print_error("Socket is not connected!")
		return False

	def send(self, data):
		try:
			self.sock.send(data)
			return True
		except Exception:
			print_error("Socket is not connected!")
		return False

	def recv(self, size):
		try:
			return self.sock.recv(size)
		except Exception:
			print_error("Socket is not connected!")
		return b""

	def recv_until(self, delimiter):
		try:
			data = b""
			while True:
				data += self.sock.recv(1)
				if delimiter in data:
					return data
		except Exception:
			print_error("Socket is not connected!")
			return b""

	def recv_all(self):
		try:
			data = b""
			while True:
				data += self.sock.recv(1)
				if not data:
					return data
		except Exception:
			print_error("Socket is not connected!")
			return b""

class Tcp_client(BaseModule):

	tcp_host = OptString("127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", "no")
	tcp_port = OptPort(80, "Target TCP port", "no")

	def open_tcp(host=None, port=None, timeout=10):

		tcp_host = host if host else self.tcp_host
		tcp_port = port if port else self.tcp_port

		return TCPSocket(tcp_host, tcp_port, timeout)
