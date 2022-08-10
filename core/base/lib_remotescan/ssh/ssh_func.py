import paramiko
import io
from base.config import DeathnoteConfig
import socket

class Ssh_func(object):
	
	def __init__(self, target, port, cache):

		self.target = target
		self.port = int(port)
		self.cache = cache
		self.ssh = None
		self.timeout = 4
		self.my_config = DeathnoteConfig()

	def ssh_login(self, user='', password=''):
		if user == "" and password == "":
			user = self.my_config.get_config('REMOTESCAN','user')
			password = self.my_config.get_config('REMOTESCAN','password')
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			self.ssh.connect(self.target, self.port, user, password, look_for_keys=False, allow_agent=False, timeout=self.timeout)
		except:
			self.ssh = None
		return self.ssh			

	def ssh_login_rsa(self, user,  key_rsa):

		not_really_a_file = io.StringIO(key_rsa)
		private_key = paramiko.RSAKey.from_private_key(not_really_a_file)

		not_really_a_file.close()

		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			self.ssh.connect(self.target, self.port, user, pkey=private_key, look_for_keys=False, allow_agent=False, timeout=self.timeout)
		except:
			self.ssh = None
		return self.ssh		

	def ssh_login_dsa(self, user, key_dsa):

		not_really_a_file = io.StringIO(key_dsa)
		private_key = paramiko.DSSKey.from_private_key(not_really_a_file)

		not_really_a_file.close()

		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			self.ssh.connect(self.target, self.port, user, pkey=private_key,look_for_keys=False, allow_agent=False, timeout=self.timeout)
		except:
			self.ssh = None
		return self.ssh		

	def get_banner(self):
		s = socket.socket()
		s.connect((self.target, self.port))
		banner = s.recv(1024).strip()
		return banner.decode()
	
	def close(self):
		self.ssh.close()
		
