from base.config import DeathnoteConfig
import requests
import socket
import urllib3
import socket
import logging
import warnings
import re

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Http_func(object):
	
	def __init__(self, target, port, cache, ssl=False):
		self.target = target
		self.port = port
		self.cache = cache
		self.my_config = DeathnoteConfig()
		self.timeout = 5
		self.ssl = ssl


	def http_request(self, method: str, path: str, session: requests = requests, headers = {}, **kwargs) -> requests.Response:
		if self.port == 80 or self.port == 443:
			if path == "/" or not path:
				if self.cache:
					return self.cache
					
		if self.ssl:
			url = f"https://{self.target}:{self.port}{path}"
		else:
			url = f"http://{self.target}:{self.port}{path}"

		if not headers:
			kwargs.setdefault("headers", {"User-agent": self.my_config.get_config('WEB','user-agent')})
		else:
			kwargs.setdefault("headers", headers)
		kwargs.setdefault("timeout", self.timeout)
		kwargs.setdefault("verify", False)
		kwargs.setdefault("allow_redirects", False)

		try:
			return getattr(session, method.lower())(url, **kwargs)
		except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
			return False
		except requests.exceptions.ConnectionError:
			return False
		except requests.exceptions.ReadTimeout:
			return False
		except requests.RequestException as e:
			return False
		except socket.error:
			return False
		
	def matchSource(self, r, match):
		pass		

	def matchHeader(self, r, headermatch):
		header, match = headermatch
		headerval = r.headers.get(header)
		if headerval:
			if header == 'Set-Cookie':
				headervals = headerval.split(', ')
			else:
				headervals = [headerval]
			for headerval in headervals:
				if re.search(match, headerval, re.I):
					return True
		return False

	def matchStatus(self, r, statuscode):
		if r.status_code == statuscode:
			return True
		return False

	def matchContent(self, r, regex):
		if re.search(regex, r.text, re.I):
			return True
		return False

	def matchCookie(self, r, match):
			return self.matchHeader(r,('Set-Cookie', match))		
