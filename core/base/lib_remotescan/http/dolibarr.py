import re
from core.base.lib_remotescan.http.http_func import Http_func

class Dolibarr(Http_func):
	
	list_dir = ['/',
             	'/dolibarr',
              	'/dolibarr/htdocs',
               	'/htdocs', 
                '/html/dolibarr', 
                '/html/dolibarr/dolibarr',
                '/html/dolibarr/dolibarr/htdocs', 
                '/dolibarr2']

 
	def is_dolibarr(self):

		for i in self.list_dir:
			try:
				r = self.http_request(
						method = "GET",
						path = i,
						allow_redirects = True
						)
				if self.matchCookie(r, 'DOLSESSID'):
					return self.target+i
				if 'DOLSESSID' in r.text:
					return self.target+i
				if 'Dolibarr' in r.text:
					return self.target+i
			except:
				continue
		return False
		
			
	def version(self):

		for i in self.list:
			try:
	#			self.url = self.target+i+'/index.php'
				r = self.http_request(
							method = "GET",
							path = i,
							allow_redirects = True
							)
				if r.status_code == 200 and 'Index of' not in r.text:
					data = re.findall(r"Dolibarr ([0-9]+.[0-9]+.[0-9]+)",r.text)
					if data:
						for d in data:
							version = d
						return version

					data = re.findall(r"Dolibarr:</b> ([0-9]+.[0-9]+.[0-9]+)",r.text)
					if data:
						for d in data:
							version = d
						return version
						
					data = re.findall(r"[0-9]+.[0-9]+.[0-9]+",r.text)
					if data:
						for d in data:
							version = d
						return version
			except:
				pass
