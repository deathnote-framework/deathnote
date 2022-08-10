from core.base.base_module import BaseModule
from core.base.option import OptString, OptPort
from core.utils.printer import *
from core.jobs import Jobs

import threading
import http.server
import socketserver
import os

class Http_server(BaseModule):
	
	srvhost = OptString("127.0.0.1", "Local http serveur address: 192.168.1.1", "yes")
	srvport = OptPort(11111, "Local http port", "yes")
	
	template_http = ""
	
	def web_delivery(self, data, forever=False, background=False):
		

		def get(self):
			if self.path == "/":
				print_status(f"Connecting to {self.client_address[0]}...")
				print_status("Sending payload stage...")

				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.write_response(bytes(data, "utf8"))

		return self.listen_http({"GET": get}, forever=forever, background=background)
	
	def _check_if_port_busy(self, lport):

		import socket, errno
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.bind(("127.0.0.1", int(lport)))
		except socket.error as e:
			if e.errno == errno.EADDRINUSE:	
				print_error("Port busy, please select another srvport option")
				return False	
		return True
	
	def listen_http(self, methods = {}, forever=False, background=False):
		""" Listen http server """
		
		if self._check_if_port_busy(self.srvport):
			try:
				for method in methods:
					setattr(Handler, f"do_{method.upper()}", methods[method])
				Handler.template_http = self.template_http
				httpd = socketserver.TCPServer((self.srvhost, self.srvport), Handler)

				if forever:
					j = Jobs()
					j.create_job("web delivery", f"http://{self.srvhost}:{self.srvport}", httpd.serve_forever, [])
				else:
					if background:
						j = Jobs()
						j.create_job("web delivery", f"http://{self.srvhost}:{self.srvport}", httpd.handle_request, [])
					else:
						httpd.handle_request()
				print_success(f"Http server created at http://{self.srvhost}:{self.srvport}")	

				return self.srvhost, httpd.server_address[1], httpd	

			except Exception:
				return False
		return False	
		

class Handler(http.server.SimpleHTTPRequestHandler):
	
	template_http = ""
	
	def log_request(self, fmt, *args):
		return

	def send_status(self, code=200):
		self.send_response(int(code))
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def write_response(self, data):
		self.wfile.write(bytes(data, "utf-8"))
	
	def write_file(self, filename):
		if os.path.exists(self.template_http + filename):
			with open(self.template_http + filename, 'rb') as f:
				self.wfile.write(f.read())

	def get_post_data(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		return post_data

	def redirect(self, url):
		self.send_response(301)
		self.send_header('Location',url)
		self.end_headers()

	def do_GET(self):
		pass
	
	def do_POST(self):
		pass
	
	def do_PUT(self):
		pass
	
	def do_HEAD(self):
		pass
