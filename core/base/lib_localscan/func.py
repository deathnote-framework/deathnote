from core.storage import LocalStorage

class Func(object):

	def __init__(self, session):
     
		self.local_storage = LocalStorage()
		sessions = self.local_storage.get("sessions")
		self.session = sessions[int(session)]
		self.handler = self.session['handler']
		self.platform = self.session['platform']
		self.version = self.session['version']
		self.os = self.session['os']
		self.type_connection = self.session['type']
	
	def send(self, data):
		""" Send data to the target """
  
		if self.type_connection == 'ssh':
			stdin,stdout,stderr=self.handler.exec_command(data)
			outlines=stdout.readlines()
			resp=''.join(outlines)
			return resp.strip()		
		else:			
			data = data+'\n'
			self.handler.settimeout(2)
			self.handler.send(data.encode())
			d = self.handler.recv(4096)
			return d.decode(errors="ignore").strip()

