import re
from core.base.lib_remotescan.http.http_func import Http_func
from bs4 import BeautifulSoup

class Wordpress(Http_func):
	
#	def __init__(self):
#		super(Wordpress).__init__()
#		self.page = None
			
	def is_wordpress(self):
		self.tag = [r'<meta name="generator" content="WordPress',
					r'<a href="http://www.wordpress.com">Powered by WordPress</a>',
					r'<link rel=\'https://api.w.org/\'',
					r'\\?\/wp-content\\?\/plugins\/|\\?\/wp-admin\\?\/admin-ajax.php']

		try:
			r = self.http_request(
					method = "GET",
					path = "/",
					allow_redirects = True,
					)
			if r:
				for i in self.tag:
					if re.search(i, r.text):
						return self.target
		except:
			print("error in is_wordpress")	

	
	def check_plugin(self, plugin):
		try:
#			else:
			r = self.http_request(
						method = "GET",
						path = '/',
						)				
			soup = BeautifulSoup(r.text, 'html.parser')
			linktags = soup.find_all('link')
			for link in linktags:
				plugin_full_link = link.get('href')
				if plugin_full_link is not None:
					if '/wp-content/plugins/' in plugin_full_link:
						plugin_split_link = plugin_full_link.split('?')[0] if '?' in plugin_full_link else plugin_full_link
						plugin_name = plugin_split_link.split('/')[5]
						plugin_version = (plugin_full_link.split('?')[1]).replace('ver=','') if '?' in plugin_full_link else 'Unknown'
#						print(plugin + '|' + plugin_name)
						if plugin == plugin_name:
#							print(plugin_version)
							return plugin_version
							
				plugin_full_link = link.get('src')
				if plugin_full_link is not None:
					if '/wp-content/plugins/' in plugin_full_link:
#						print('---------------')
						plugin_split_link = plugin_full_link.split('?')[0] if '?' in plugin_full_link else plugin_full_link
						plugin_name = plugin_split_link.split('/')[5]
						plugin_version = (plugin_full_link.split('?')[1]).replace('ver=','') if '?' in plugin_full_link else 'Unknown'
#						print(plugin + '|' + plugin_name)
						if plugin == plugin_name:
#							print(plugin_version)
							return plugin_version

			r = self.http_request(
						method = "GET",
						path = '/wp-content/plugins/'+plugin+'/readme.txt',
						)
#			if plugin == 'contact-form-7':
#				print('---------------')
#				print(r.status_code)			
			if r.status_code == 200:
				v = self.getVersion("Stable tag: ([0-9.]+)", r.text)
				if v:
					return v
				v = self.getVersion("Tested up to: ([0-9.]+)", r.text)
				return v

		except:
			return False
	
	def check_theme(self, theme):	
		try:
			r = self.http_request(
						method = "GET",
						path = '/',
						)				
			soup = BeautifulSoup(r.text, 'html.parser')
			linktags = soup.find_all('link')
			for link in linktags:
				theme_full_link = link.get('href')
				if theme_full_link is not None:
					if '/wp-content/themes/' in theme_full_link:
						theme_split_link = theme_full_link.split('?')[0] if '?' in theme_full_link else theme_full_link
#						print(plugin_split_link)
						theme_name = theme_split_link.split('/')[5]
						theme_version = (theme_full_link.split('?')[1]).replace('ver=','') if '?' in theme_full_link else 'Unknown'
						if theme == theme_name:
							return theme_version
		except:
			return False
	def version(self):

		try:
			r = self.http_request(
					method = "GET",
					path = "/",
					)
			if r.status_code == 200 and r.content != ("" or None):
				version = re.findall(r'<meta name="generator" content="WordPress (\d+\.\d+[\.\d+]*)"',r.text)
				if version:
					return version[0]
		except:
			pass

		try:
			r = self.http_request(
					method = "GET",
					path = "/wp-links-opml.php",
					)
			if r.status_code == 200 and r.content != ("" or None):
				version = re.findall(r'\S+WordPress/(\d+.\d+[.\d+]*)',r.text)
				if version:
					return version[0]
		except:
			pass
		
		try:
			r = self.http_request(
					method = "GET",
					path = "/feed",
					)
			if r.status_code == 200 and r.content != ("" or None):
				version = re.findall(r'\S+?v=(\d+.\d+[.\d+]*)',r.text)
				if version:
					return version[0]
		except:
			pass
		
		try:
			r = self.http_request(
					method = "GET",
					path = "/feed/atom",
					)
			if r.status_code == 200 and r.content != ("" or None):
				version = re.findall(r'<generator uri="http://wordpress.org/" version="(\d+\.\d+[\.\d+]*)"',r.text)
				if version:
					return version[0]
		except:
			pass				

		try:
			r = self.http_request(
					method = "GET",
					path = "/readme.html",
					)
			if r.status_code == 200 and r.content != ("" or None):
				version = re.findall(r'*wordpress-logo.png" /></a>\n.*<br />.* (\d+\.\d+[\.\d+]*)\n</h1>',r.text)
				if version:
					return version[0]
		except:
			pass	
