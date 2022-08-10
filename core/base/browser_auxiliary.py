from core.base.base_module import BaseModule
from core.utils.printer import *
from core.sessions import Sessions
from core.base.option import *
from core.storage import LocalStorage

class BrowserAuxiliary(BaseModule):

	type_module = "browser_auxiliary"
	session = OptSession(0, 'Session number', 'no')
	
	def __init__(self):
		super(BrowserAuxiliary, self).__init__()

	def detect_os(self):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(self.session)]
		return session['os']
 
	def run(self):
		raise NotImplementedError("You have to define your own 'run' method.")	
	
	def exploit(self):
		self.run()

	def send_js(self, data):
			
		shell = Sessions()
		shell.execute(self.session, data)
    
