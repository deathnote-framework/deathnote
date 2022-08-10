from core.base.base_module import BaseModule
from core.base.option import *
from core.utils.printer import *
from core.jobs import Jobs
from core.sessions import Sessions
from core.utils.function import *
import inspect, os

class Listener(BaseModule):

	type_module = "listener"

	def __init__(self):
		super(Listener, self).__init__()
	
	def run(self):
		raise NotImplementedError("You have to define your own 'send_protocol' method.")

	def close(self, sock=None):
		pass

	def exploit(self):
		""" Run listener """
		handler = self.run()
		if handler:
			if "session" not in self._Module__info__.keys():
				print_error("Option session not in __info__, please add this")
				return False
			listener_path = inspect.getfile(self.__class__).replace(os.getcwd()+"/modules/","")[:-3]
			session = Sessions()
			session.add_session(
						session_arch="",
						session_os="",
						session_version="",
						session_type=self._Module__info__['session'],
						session_host=handler[1][0],
						session_port=handler[1][1],
						session_handler=handler[0],
						session_user="",
						session_listener=listener_path,
						session_option=self.exploit_attributes
			)
			print_success("Session opened")
			return True
		else:
			return False