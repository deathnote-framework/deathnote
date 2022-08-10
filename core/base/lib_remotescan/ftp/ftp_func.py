from base.config import DeathnoteConfig
import ftplib
import re

class Ftp_func(object):

	def __init__(self, target, port, cache):

		self.target = target
		self.port = int(port)
		self.cache = cache
		self.ftp_client = ftplib.FTP()
		self.config = configparser.ConfigParser()
		self.config.read('deathnote/config/config.ini')
		
		
	def banner(self):
		try:

			banner = self.ftp_client.connect(self.target, self.port, 4.0)
			return banner
		except:
			self.ftp_client.close()
			return False
	
	def ftp_login(self, user="", password=""):
		if user == "" and password == "":
			user = self.config['VULNSCAN']['User']
			password = self.config['VULNSCAN']['Password']
		try:
			self.ftp_client.connect(self.target, self.port, 2.0)
			self.ftp_client.login(user, password)
			return self.ftp_client
		except Exception:
			self.ftp_client.close()
			return False
		

	def is_proftpd(self, banner):
		if "ProFTPD" in banner:
			return True
		return False
	
	def version_proftpd(self, banner):
		v = re.search(r'ProFTPD \s*([\d\w.]+)',banner)
		if v:
			return v.group(1)
