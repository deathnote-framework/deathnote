from core.base.base_module import BaseModule
from core.base.option import OptString, OptPort, OptFile
from core.utils.printer import *

import paramiko
import io

class Ssh_lib:

	def __init__(self, host, port, user, password):
		
		self.ssh_target = host
		self.ssh_port = port
		self.ssh_user = user
		self.ssh_password = password
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	def login(self, user='', passwd=''):
		if user == '':
			user = self.ssh_user
		if passwd == '':
			passwd = self.ssh_password

		try:
			self.ssh.connect(self.ssh_target, self.ssh_port, user, passwd, look_for_keys=False, allow_agent=False)
		except paramiko.AuthenticationException as e:
			print_error(e)	
			self.ssh = None
		except paramiko.ssh_exception.NoValidConnectionsError as e:
			print_error(e)				
			self.ssh = None
		except:
			self.ssh = None
		return self.ssh

	def login_rsa(self, key_rsa):

		not_really_a_file = io.StringIO(key_rsa)
		private_key = paramiko.RSAKey.from_private_key(not_really_a_file)

		not_really_a_file.close()

		try:
			self.ssh.connect(self.ssh_target, self.ssh_port, self.username, pkey=private_key)
		except paramiko.AuthenticationException as e:
			print_error(e)	
			self.ssh = None   
		except paramiko.ssh_exception.NoValidConnectionsError as e:
			print_error(e)	
			self.ssh = None			
		except:
			self.ssh = None
		return self.ssh		

	def login_dsa(self, key_dsa):

		not_really_a_file = io.StringIO(key_dsa)
		private_key = paramiko.DSSKey.from_private_key(not_really_a_file)

		not_really_a_file.close()

		try:
			self.ssh.connect(self.ssh_target, self.ssh_port, self.username, pkey=private_key)
		except paramiko.AuthenticationException as e:
			print_error(e)	
			self.ssh = None   
		except paramiko.ssh_exception.NoValidConnectionsError as e:
			print_error(e)	
			self.ssh = None			
		except:
			self.ssh = None
		return self.ssh		

	def send_command(self, command):        
		try:
			return self.ssh.exec_command(command)
		except Exception:
			raise RuntimeError(f"Socket {self.ssh_host}:{self.ssh_port} is not connected!")

	def close(self):
		self.ssh.close()
   
class Ssh_client(BaseModule):
       
	ssh_target = OptString("", "Target IPv4 or IPv6 address", "no")
	ssh_port = OptPort(22, "Target SSH port", "no")
	ssh_user = OptString("root", "ssh username", "no")
	ssh_password = OptString("root", "ssh password", "no")

	key_rsa = OptFile("", "filename with rsa key", "no", True)
	dsa_rsa = OptFile("", "filename with dsa key", "no", True)
 
	def open_ssh(self, host=None, port=None, user=None, password=None):

		ssh_host = host if host else self.ssh_target
		ssh_port = port if port else self.ssh_port
		ssh_user = user if user else self.ssh_user
		ssh_pass = password if password else self.ssh_password

		client = Ssh_lib(ssh_host, ssh_port, ssh_user, ssh_pass)
		return client