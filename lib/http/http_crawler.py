from core.base.base_module import BaseModule
from core.base.option import OptString, OptInteger, OptPort, OptBool
from core.utils.printer import *
from nyawc.Options import Options as Options_crawler
from nyawc.Crawler import Crawler as nyawcCrawler
from nyawc.CrawlerActions import CrawlerActions
from nyawc.http.Request import Request
from nyawc.QueueItem import QueueItem
import pathlib
import urllib
from requests.auth import HTTPBasicAuth

class Http_crawler(BaseModule):
	
	target = OptString("mytarget.com", "Target domain/ip", "yes")
	port = OptPort(80, "Target HTTP port", "yes")
	ssl = OptBool(False, "SSL enabled: true/false","no",True)
	max_crawl = OptInteger(20, "Number of links to crawling, (if 0 = all link)", True)
	max_threads = OptInteger(20, "Maximum number of threads", True)
	request_timeout = OptInteger(15, "Timeout", True)
	crawler_user = OptString("admin", "User ", True)
	crawler_password = OptString("admin", "Password ", True)

	def crawler_start(self):
		if not self.target.startswith("http"):
			if self.ssl:
				if not self.target.startswith("https://"):
					self.target = "https://"+self.target
			else:
				if not self.target.startswith("http://"):
					self.target = "http://"+self.target
     			
		if int(self.port) != 80 or int(self.port) != 443:
			target = self.target+":"+str(self.port)
		else:
			target = self.target

		u = urllib.parse.urlsplit(self.target)
		if u.path == '':
			self.target += "/"

		crawler = Crawler_core(max_threads=self.max_threads,
								max_crawl=self.max_crawl,
								request_timeout=self.request_timeout,
								user=self.crawler_user,
								password=self.crawler_password)
		
		crawler.crawler.start_with(Request(target))
		self._output += crawler.links

class Crawler_core:

	def __init__(self, max_threads=1, max_crawl=0, request_timeout=15, user="admin", password="admin"):
		self.links = []
		self.crawler = None
		self.max_threads = max_threads
		self.max_crawl = max_crawl
		self.request_timeout = request_timeout
		self.crawler_user = user
		self.crawler_password = password
		self.config_crawler()
		self.ignored_extensions=["gif","jpg","png","css","jpeg","woff","ttf","eot","svg","woff2","ico"]
		self.js_extensions=["js"]
		self.static_extensions=["html","htm","xhtml","xhtm","shtml", "txt"]
		self.scripts_extensions=["php","jsp","asp","aspx","py","pl","ashx","php1","php2","php3","php4"]
		self.cpt = 0

	def config_crawler(self):

		options_crawler = Options_crawler()
		options_crawler.scope.max_depth = 4
		options_crawler.scope.request_methods = [
			Request.METHOD_GET,
			Request.METHOD_POST,
			Request.METHOD_PUT,
			Request.METHOD_DELETE,
			Request.METHOD_OPTIONS,
			Request.METHOD_HEAD
		]

		options_crawler.callbacks.crawler_before_start = self.crawlerstart
		options_crawler.callbacks.crawler_after_finish = self.crawlerfinish
		options_crawler.callbacks.request_before_start = self.requeststart
		options_crawler.callbacks.request_after_finish = self.requestfinish

		options_crawler.performance.max_threads = self.max_threads
		options_crawler.performance.request_timeout = self.request_timeout
		options_crawler.scope.protocol_must_match = False
		options_crawler.scope.subdomain_must_match = False
		options_crawler.scope.hostname_must_match = True
		options_crawler.identity.auth = HTTPBasicAuth(self.crawler_user, self.crawler_password)
		options_crawler.routing.minimum_threshold = 20
		self.crawler = nyawcCrawler(options_crawler)
		
	def get_links(self):
		return self.links

	def extension(self, str):
		if "?" in str:
			str=str[0:str.find("?")]
		str=pathlib.Path(str).suffix
		return str[1:len(str)]

	def crawlerstart(self):
		""" Called before the crawler starts crawling. Default is a null route."""
		print_status("Crawler started")

	def crawlerfinish(self, queue):
		""" Called after the crawler finished crawling. Default is a null route."""
		print_status("Crawler finished")

	def requeststart(self, queue, queue_item):
		""" Called before the crawler starts crawling. Default is a null route."""
		if self.extension(queue_item.request.url).lower() in self.ignored_extensions: # Don't crawl gif, jpg , etc
			return CrawlerActions.DO_SKIP_TO_NEXT		

	def requestfinish(self, queue, queue_item, new_queue_items):
		""" Called after the crawler finished crawling. Default is a null route."""
		url = queue_item.request.url
		method = queue_item.request.method
		extension = self.extension(url).lower()
		if not url in self.links:
			if self.cpt == self.max_crawl and self.max_crawl != 0:
				print_status(f"{self.cpt} links found")
				return CrawlerActions.DO_STOP_CRAWLING
			else:
				if extension in self.js_extensions :
					print_status("JS > "+url)
				elif self.extension(url).lower() in self.static_extensions :
					print_status("HTML > "+url)
				elif self.extension(url).lower() in self.scripts_extensions :
					print_status("Serverscript > "+url)
					if method == "post":
						print_info('\t'+queue_item.request.data)
				else:
					print_status("Other > "+url)
				self.links.append(url)
				self.cpt += 1
		return CrawlerActions.DO_CONTINUE_CRAWLING
