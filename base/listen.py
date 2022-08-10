from core.utils.printer import *
import socket
from threading import Thread
import threading
import time

class Listen:
	
	def __init__(self, port):
		self.lock = threading.Lock()
		self.s = socket.socket()
		self.conn = None
		self.stop_threads = False
		self.port = port
		self.stop_loop = True
  
	def initialize(self):
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.s.bind(('0.0.0.0', self.port))
			print_success(f"Listening on :{self.port}")
			return True
		except:
			print_error(f"You must be root to bind port {self.port}")
			return False

	def listen(self):
		self.s.listen(1)
		try:
			self.conn, addr = self.s.accept()
			self.conn.settimeout(3)
			print_success(f"Connection established: {addr[0]}")
			recv = Thread(target=self.recv)
			recv.start()   
		except OSError:
			if self.lock.acquire():
				self.lock.release()
    
	def recv(self):

		while True:
			if self.stop_threads:
				try:
					if self.conn:
						self.conn.close()
						self.s.close()
					break
				except OSError:
					pass
			elif self.conn:
				try:
					data = self.conn.recv(4096)
					if data:
						print_info(data.decode(errors="ignore").strip())
				except socket.timeout:
					pass	
				except OSError:
					if self.conn is not None:
						self.conn.close()
						self.s.close()
					break
			else:
				time.sleep(1)

	
	def run(self):
		init = self.initialize()
		if init:
			listen = Thread(target=self.listen)
			listen.start()	
			while self.stop_loop:
				data = input()
				if self.conn:
					if data == "exit":
						print_success("Exit listener")
						self.stop_threads = True
						self.s.shutdown(2)
						self.s.close()
						break
					data = data + "\n"
					self.conn.send(data.encode())
				else:
					if data == "exit":
						self.s.shutdown(2)
						self.s.close()
						break
					print_status("Wait client...")
     
	def stop(self):
		self.stop_threads = True
		self.stop_loop = False
		self.s.shutdown(2)
		self.s.close()