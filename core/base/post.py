from core.base.base_module import BaseModule
from core.base.option import *
from core.utils.printer import *
from core.storage import LocalStorage
from core.jobs import Jobs
from core.sessions import Sessions
import importlib
import time

class Post(BaseModule):
	
	session = OptSession(0, "session", "no")
	
	def __init__(self):
		super(Post, self).__init__()
		self.jobs = Jobs()
		self.local_storage = LocalStorage()
		self._sessions = self.local_storage.get("sessions")
		self.prompt = ""
		self.payload_options = []
		self._current_payload = None
		self._current_encoder = None	
		self.type_module = "post"	
		
	def run(self):
		raise NotImplementedError("You have to define your own 'send_protocol' method.")

	def info_payload(self,  info):
		if self._current_payload:
			if info in self._current_payload._Module__info__:
				return self._current_payload._Module__info__[info]
		return

	def _check_if_port_busy(self, lport):
		import socket, errno
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.bind(("127.0.0.1", int(lport)))
		except socket.error as e:
			if e.errno == errno.EADDRINUSE:	
				print_error("Port busy, please select another lport option")
				return False	
		return True

	def exploit(self):
		if self.current_session('platform') == 'Unknow':
			print_status(f"No platform found, try: sessions -c {self.session}")
			return
		if self.type_module == "exploit_local":
			if self._current_payload:
				if 'type' in self._current_payload._Module__info__:
					if self._current_payload._Module__info__['type'] == 'reverse':
						if self._current_payload._Module__info__['handler'] is not None:
							if self._check_if_port_busy(self.exploit_attributes['lport'][0]):
							
								prepare_handler = pythonize_path(self._current_payload._Module__info__['handler'])
								handler = getattr(importlib.import_module("modules."+prepare_handler), "Module")()
								setattr(handler, 'lhost', self.exploit_attributes['lhost'][0])
								handler.exploit_attributes['lhost'][0] = self.exploit_attributes['lhost'][0]
								setattr(handler, 'lport', self.exploit_attributes['lport'][0])
								handler.exploit_attributes['lport'][0] = self.exploit_attributes['lport'][0]	
								handler.payload_selected = self._current_payload._Module__info__['platform']
								self.jobs.create_job("Reverse tcp", f":{self.lport}", handler.exploit, [])
								time.sleep(1)
								code_execution = self.run()
							return
				
					if self._current_payload._Module__info__['type'] == 'bind':
						if self._current_payload._Module__info__['handler'] is not None:
							code_execution = self.run()
							if code_execution:
								prepare_handler = pythonize_path(self._current_payload._Module__info__['handler'])
								handler = getattr(importlib.import_module("modules."+prepare_handler), "Module")()
								setattr(handler, 'rhost', self.exploit_attributes['rhost'][0])
								handler.exploit_attributes['rhost'][0] = self.exploit_attributes['rhost'][0]					
								setattr(handler, 'rport', self.exploit_attributes['rport'][0])
								handler.exploit_attributes['rport'][0] = self.exploit_attributes['rport'][0]	
								handler.exploit()
							return		
		else:
			self.run()
	
	def current_session(self, data):
		self._sessions = self.local_storage.get("sessions")
		s = self._sessions[int(self.session)]
		if data in s.keys():
			return s[data]
		return ""

	def cmd_exec(self, command, output=True, timeout=2):
		s = Sessions()
		result = s.execute(self.session, command)
		if output:
			return result