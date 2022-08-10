from core.base.base_module import BaseModule
from core.base.option import OptBool, OptPort, OptString
from core.utils.printer import *
import smtplib

class Smtp_lib:

	
	def __init__(self, host, port, user, password):

		self.smtp_host = host
		self.smtp_port = port
		self.smtp_user = user
		self.smtp_pass = password
		self.smtp_client = smtplib.SMTP()
	

	def connect(self):
		try:
			(code, banner) = self.smtp_client.connect(self.smtp_host, self.smtp_port, 8.0)
			return (code, banner)
		except:
			self.smtp_client.close()
			return False
	
	def login(self, user='', password=''):
		if user == '':
			user = self.smtp_user
		if password == '':
			password = self.smtp_pass
		try:
			self.smtp_client.login(user, password)		
			return self.smtp_client
		except Exception:
			self.smtp_client.close()
			return False
		
	def send_mail(self, data, from_addr='', to_addr=''):
			self.smtp_client.sendmail(from_addr, to_addr, data)
			print_status('Email sending')
	
	def smtp_quit(self):
		self.smtp_client.quit()
		
class Smtp_client(BaseModule):

	smtp_host = OptString("127.0.0.1", "smtp host", "yes")
	smtp_port = OptPort(25, "smtp port", "yes")
	smtp_user = OptString("test@test.com", "smtp user", "no")
	smtp_pass = OptString("user", "smtp pass", "no")
 
	def open_smtp(self, host=None, port=None, user=None, password=None):

		smtp_host = host if host else self.smtp_host
		smtp_port = port if port else self.smtp_port
		smtp_user = user if user else self.smtp_user
		smtp_pass = password if password else self.smtp_pass
 
		client = Smtp_lib(smtp_host, smtp_port, smtp_user, smtp_pass)
		return client