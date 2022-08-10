from core.base.base_module import BaseModule
from core.base.option import OptString, OptPort, OptBool
from core.utils.printer import *

import requests
import urllib3
from bs4 import BeautifulSoup
import socket
import logging
import warnings
from random import choice

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Http_client(BaseModule):
	
	target = OptString("127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", "yes")
	port = OptPort(80, "Target HTTP port", "yes")
	ssl = OptBool(False, "SSL enabled: true/false","no",True)
	user_agent = OptString("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)", "The User-Agent header to use for all requests", "no", True)
	uripath = OptString("/", "Path", "yes")

	def __init__(self):
		super().__init__()
		self.session = requests.Session()
	
	def http_request(self, method="GET", host=None, port=None, path='/', ssl=False, timeout=8, output=True, session=False, **kwargs):
		"""This method do a http/https request
		
        argument: 	method --> required
                    host=None (if none, target option is take)
                    port=None (if none, port option is take)
                    path = '/'
                    ssl=False
                    session=False
        return:     response object
		"""


		if not host:	
			url = self._normalize_url(self.target, self.port, path, self.ssl)		
		else:
			if not port:
				port = self.port
			url = self._normalize_url(host, port, path, ssl)
		
		if session:
			session = self.session
		else:
			session = requests
	
		kwargs.setdefault("timeout", timeout)		
		kwargs.setdefault("verify", False)
		kwargs.setdefault("allow_redirects", True)	

		try:
			return getattr(session, method.lower())(url, **kwargs)
		except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
			print_error("Invalid URL format: {}!".format(url))
		except requests.exceptions.ConnectionError:
			print_error("Connection error: {}!".format(url))
		except requests.exceptions.ReadTimeout:
			print_warning("Timeout waiting for response.")
		except requests.RequestException as e:
			print_error("Request error: {}!".format(str(e)))
		except socket.error:
			print_error("Socket is not connected!")
		except Exception as e:
			print_error("Error: {}!".format(str(e)))

		return None		

	def _normalize_url(self, host, port, path, ssl=False):
		"""This method normalize url"""
		url = ""
		if ssl:
			if not host.startswith("https://"):
				url = "https://"
		else:
			if not host.startswith("http://"):
				url = "http://"

		url += "{}:{}{}".format(host, port, path)
		return url

	def _http_test_connect(self):
		""" Test connection to HTTP server

     		return:   Boolean (True if test connection was successful, False otherwise)
		"""

		response = self._http_request(
			method="GET",
			path="/"
		)
		if response:
			return True
		return False
	
	def _wget(self, url, save=False, timeout=5, **kwargs):
		"""This method download url file
		argument:    url
		             save=False (save in file)
		             timeout=5  (timeout for request)
		return:      content data

		"""
		print_status("Making request...")
		response = requests.get(url, stream=True, timeout=timeout, **kwargs)
		if not response.ok:
			print_error(f"Download failed: error {response.status_code}")
			return

		total_size = int(response.headers.get('content-length',0))
		total_data = response.content
		if save:
			with open("output/save",'wb+') as f:
				f.write(total_data)
				print_success('Saved %r (%s)' % (f.name, size(total_data)))
		else:
			print_success(f"size: {total_data}")
		return total_data		

	def url_encode(self, data):
		"""This method encode data to url format"""
		r = urllib.parse.quote(data, safe='')
		return r

	def extract_link(self, resp):
		"""This method extract link from response"""
		links = []
		source={'a':'href', 'script':'src', 'link':'href'}
		soup = BeautifulSoup(resp.text, 'html.parser')
		for tag in source.keys():
			for link in soup.find_all(tag):
				if link.get(source[tag]):
					links.append(link.get(source[tag]))
		return links

	def extract_headers(self, resp, header):
		"""This method extract header from response"""
		return resp.headers.get(header)


	def random_agent(self):
		"""This method generate random user-agent"""
		user_agent = [
		'''Mozilla/5.0 (Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.55''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.37''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57''',
		'''Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/63.0''',
		'''Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36 OPR/48.0.2685.52''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36 OPR/49.0.2725.64''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.58''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0''',
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0''',
		'''Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko''',
		'''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (Windows NT 9.0; WOW64; Trident/7.0; rv:11.0) like Gecko''',
		'''Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27''',
		'''Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0''',
		'''Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0''',
		'''Mozilla/5.0 (X11; Linux i686; rv:78.0) Gecko/20100101 Firefox/78.0''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.49 Safari/537.36 OPR/48.0.2685.7''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57''',
		'''Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (X11; U; Linux x86_64; en-us) AppleWebKit/531.2+ (KHTML, like Gecko) Version/5.0 Safari/531.2''',
		'''Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:78.0) Gecko/20100101 Firefox/78.0''',
		'''Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0''',
		'''Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0''',
		]  
		return choice(user_agent)