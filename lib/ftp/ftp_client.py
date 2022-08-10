from core.base.base_module import BaseModule
from core.base.option import OptBool, OptPort, OptString
from core.utils.printer import *
import ftplib


class Ftp_lib:

	
	def __init__(self, host, port, user, password, ssl):
		
		self.ftp_host = host
		self.ftp_port = port
		self.ftp_user = user
		self.ftp_password = password
		self.ftp_ssl = ssl		
  
		if self.ftp_ssl:
			self.ftp_client = ftplib.FTP_TLS()
		else:
			self.ftp_client = ftplib.FTP()

	def connect(self):
		try:
			self.ftp_client.connect(self.ftp_host, self.ftp_port, 8.0)
			return True
		except:
			self.ftp_client.close()
			return False
	
	def login(self, user='', password=''):
		if user == '':
			user = self.ftp_user
		if password == '':
			password = self.ftp_pass
		try:
			self.connect()
			self.ftp_client.login(user, password)
			return True
		except Exception:
			self.ftp_client.close()
			return False

	def close(self):

		try:
			self.ftp_client.close()
			return True
		except:
			return False

class Ftp_client(BaseModule):
    
	ftp_host = OptString("127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", "no")
	ftp_port = OptPort(21, "Target FTP port", "no")
	ftp_user = OptString("anonymous", "Path", "no")
	ftp_pass = OptString("anonymous", "Path", "no")
	ftp_ssl = OptBool(False, "SSL enabled: true/false")
 
	def open_ftp(self, host=None, port=None, user=None, password=None, ssl=False):

		ftp_host = host if host else self.ftp_host
		ftp_port = port if port else self.ftp_port
		ftp_user = user if user else self.ftp_user
		ftp_pass = password if password else self.ftp_pass
		ftp_ssl = ssl if ssl else self.ftp_ssl

		client = Ftp_lib(ftp_host, ftp_port, ftp_user, ftp_pass, ftp_ssl)
		return client