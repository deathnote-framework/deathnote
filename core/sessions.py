from core.storage import LocalStorage
from core.browser_server.base_browser_server import socketio
from core.utils.import_module import import_exploit
from core.utils.printer import *
from core.utils.db import *
from core.utils.function import *
from http.server import BaseHTTPRequestHandler
from core.shell.javascript import Javascript
from core.shell.shell import Shell
from core.shell.shell_subprocess import Shell_subprocess
from core.shell.tty import Tty
from core.shell.ssh import Ssh
from core.shell.cmd import Cmd
from core.shell.php import Php
import time
import re
		
class Sessions:

	def __init__(self):
		self.local_storage = LocalStorage()
		if not self.local_storage.get("sessions"):
			self.local_storage.set("sessions", dict())
	
	def get_all_sessions(self):
		""" Returns all sessions """
		sessions = self.local_storage.get("sessions")
		return sessions

	def auto_run_autoattack(self, session_id):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]
		if session['type'] == 'javascript':
			socketio.emit('issue_task', {'id':int(session_id),'input': 'auto_run_autoattack', 'type':'cmd'}, room=session['handler'])
	
	def add_session(self, session_arch, session_os, session_version, session_type, session_host, session_port, session_handler, session_user="", session_listener="", session_option={}):
	
		session_id = 0
		while (session_id in self.local_storage.get("sessions") or session_id < len(self.local_storage.get("sessions"))):
			session_id += 1
		sessions = {
				session_id: {
					'name': '',
					'arch': session_arch,
					'os': session_os,
					'version': session_version,
					'type': session_type,
					'host': session_host,
					'port': session_port,
					'handler': session_handler,
					'user': session_user,
					'listener': session_listener,
					'options': session_option,
					}
				}
		self.local_storage.update("sessions", sessions)
		self.determinate(session_id)
		if self.local_storage.get("auto_attack"):
			self.auto_attack_run_background(session_id, self.local_storage.get("auto_attack"))
		return session_id

	def rename_session(self, session_id, name):
		sessions = self.local_storage.get("sessions")
		sessions[int(session_id)]["name"] = name
		self.local_storage.update(int(session_id), sessions[int(session_id)])

	def delete_session(self, session_id):
		sessions = self.local_storage.get("sessions")
		del sessions[int(session_id)]

	def kill_session(self, session_id):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]
		if session['type'] == 'shell':
			s = Shell(session_id)
			s.close()

		elif session['type'] == 'shell_subprocess':
			s = Shell_subprocess(session_id)
			s.close()

	def auto_attack_run_background(self, session_id, modules={}):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]
		type_shell = session["type"]
		for module in modules.keys():
			if module.startswith("browser_"):
				module_path = pythonize_path(module)
				module_path = ".".join(("modules",module_path))
				try:
					loaded_module = import_exploit(module_path)()
				except SyntaxError as e:
					print_error(e)
					continue
				if type_shell == "javascript":
					for option in modules[module].keys():
						
						if option == "session":
							setattr(loaded_module, "session", session_id)
						else:
							setattr(loaded_module, option, modules[module][option])
					loaded_module.run()
				else:
					continue

	def determinate(self, session_id):
		""" Determinate session info"""
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]

		if session['type'] == 'javascript':
			javascript = Javascript(session_id)
			javascript.determinate()

		if session['type'] == 'shell':
			shell = Shell(session_id)
			shell.determinate()

		if session['type'] == 'shell_subprocess':
			shell_subprocess = Shell_subprocess(session_id)
			shell_subprocess.determinate()

		if session['type'] == 'cmd':			
			cmd = Cmd(session_id)
			cmd.determinate()	
		
		if session['type'] =='powershell':
			pass

		if session['type'] =='php':
			php = Php(session_id)
			php.determinate()
  
		if session['type'] == 'tty':
			tty = Tty(session_id)
			tty.determinate()
  
		if session['type'] == 'ssh':
			ssh = Ssh(session_id)
			ssh.determinate()

	def upgrade(self, session_id):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]

		if session['type'] == 'shell':
			Shell(session_id).upgrade()
	
	def execute(self, session_id, command, raw=False):
		""" Execute a command on a session """
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]

		if session['type'] == 'javascript':
			javascript = Javascript(session_id)
			output = javascript.execute(command, raw=raw)
			return output

		if session['type'] == 'shell':
			shell = Shell(session_id)
			output = shell.execute(command, raw=raw)
			return output

		if session['type'] == 'shell_subprocess':
			shell_subprocess = Shell_subprocess(session_id)
			output = shell_subprocess.execute(command, raw=raw)
			return output

		if session['type'] == 'cmd':			
			cmd = Cmd(session_id)
			output = cmd.execute(command, raw=raw)
			return output	
		
		if session['type'] =='powershell':
			pass

		if session['type'] =='php':
			php = Php(session_id)
			output = php.execute(command, raw=raw)
			return output
  
		if session['type'] == 'tty':
			tty = Tty(session_id)
			output = tty.execute(command, raw=raw)
			return output
  
		if session['type'] == 'ssh':
			ssh = Ssh(session_id)
			output = ssh.execute(command, raw=raw)
			return output
	
	def interactive(self, session_id):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]

		if session['type'] == 'javascript':
			print_success("Session opened")
			javascipt = Javascript(session_id)
			javascipt.interactive()

		if session['type'] == 'shell':
			print_success("Session opened")
			shell = Shell(session_id)
			shell.interactive()

		if session['type'] == 'tty':
			print_success("Session opened")
			tty = Tty(session_id)
			tty.interactive()

		if session['type'] == 'shell_subprocess':
			print_success("Session opened")
			shell_subprocess = Shell_subprocess(session_id)
			shell_subprocess.interactive()

		if session['type'] == 'ssh':
			print_success("Session opened")
			ssh = Ssh(session_id)
			ssh.interactive()
						
		if session['type'] == 'cmd':
			print_success("Session opened")
			cmd = Cmd(session_id)
			cmd.interactive()
   
		if session['type'] == 'php':
			print_success("Session opened")
			php = Php(session_id)
			php.interactive()
		
		if session['type'] == 'http':
			sessions = self.local_storage.get("sessions")
			session = sessions[int(session_id)]	
			handler = session['handler']
			handler = MyHandler_().do_GET						



	def determinate_old(self, session_id):
		sessions = self.local_storage.get("sessions")
		token = "opzaxl32d3a"
		response = self.execute(session_id, f"command -v ifconfig && echo {token}")
		if token in response:
			#linux os
			new_os = sessions[int(session_id)]["os"] = "Linux"
			self.local_storage.update(int(session_id), new_os)

			whoami = self.execute(session_id,"whoami")
			if "whoami" not in whoami:
				new_session = sessions[int(session_id)]["user"] = whoami.strip()
				self.local_storage.update(int(session_id), new_session)	

			platform_arch = self.execute(session_id, "uname -m")
			print(platform_arch)
			new_platform = sessions[int(session_id)]["platform"] = platform_arch.strip()
			self.local_storage.update(int(session_id), new_platform)

			version = self.execute(session_id, "lsb_release -a")
			result = ""
			if version:
				v=re.findall(r"Description: (.*) Release", version)
				if v:
					result = v[0]
			print(result)
			new_session = sessions[int(session_id)]["version"] = result.strip()
			self.local_storage.update(int(session_id), new_session)

		else:
			response = self.execute(session_id, f"where /q ipconfig & if not errorlevel 1 echo {token}")
			if token in response:
				#windows os
				new_os = sessions[int(session_id)]["os"] = "Windows"
				self.local_storage.update(int(session_id), new_os)
    
				get_user = self.execute(session_id, "whoami")
				if "whoami" not in get_user:
					new_user = sessions[int(session_id)]["user"] = get_user
					self.local_storage.update(int(session_id), new_user)
     
				get_version = self.execute(session_id, "ver")
				if "ver" not in get_version:
					new_version = sessions[int(session_id)]["version"] = get_version
					self.local_storage.update(int(session_id), new_version)

    
			else:
				#unknown os
				pass

	def check(self, session_id):
		sessions = self.local_storage.get("sessions")
		session = sessions[int(session_id)]		
		if session['type'] == 'cmd':
			if session['platform'] == 'php':
				if not session['version']:
					execute = session['handler']
					version = execute("$v='';if(function_exists('phpversion')){$v=phpversion();}elseif(defined('PHP_VERSION')){$v=PHP_VERSION;}elseif(defined('PHP_VERSION_ID')){$v=PHP_VERSION_ID;}print($v);")
					if version:
						new_session = sessions[int(session_id)]["version"] = version
						self.local_storage.update(int(session_id), new_session)

		if session['type'] == 'shell':
			import socket
			sessions = self.local_storage.get("sessions")
			session = sessions[int(session_id)]			
			if session['platform'] == 'Unknow':
				command_list = ["uname -a", "ver", "sw_vers"]
				for command in command_list:
					handler = session['handler']
					handler.settimeout(2)
					command = command + "\n"
					handler.send(command.encode())
					try:
						data = handler.recv(4096)
					except socket.timeout:
						data = ""
					if "Linux" in data.decode(errors="ignore"):
						new_session = sessions[int(session_id)]["platform"] = "linux"
						self.local_storage.update(int(session_id), new_session)
						break
					if "Windows" in data.decode(errors="ignore"):
						new_session = sessions[int(session_id)]["platform"] = "windows"
						self.local_storage.update(int(session_id), new_session)
						break		
					if "macOS" in data.decode(errors="ignore"):
						new_session = sessions[int(session_id)]["platform"] = "macos"
						self.local_storage.update(int(session_id), new_session)
						break	
				version_list = ["lsb_release -a"]
				for command in version_list:
					handler = session['handler']
					handler.settimeout(5)
					command = command + "\n"
					handler.send(command.encode())
					time.sleep(1)
					try:
						data = handler.recv(8000)
					except socket.timeout:
						data = ""	
					if data:
						lsb_release = data.decode(errors="ignore")
						lines = lsb_release.split('\n')
						for line in lines:
							if line.startswith("Description"):
								version = line.split(':')[1].strip()
								new_session = sessions[int(session_id)]["version"] = version
								self.local_storage.update(int(session_id), new_session)		
								break	
			if session['user'] == '':
				handler = session['handler']
				handler.settimeout(2)
				command = "whoami"
				command = command + "\n"
				handler.send(command.encode())
				time.sleep(1)
				try:
					data = handler.recv(4096)
				except socket.timeout:
					data = b""
				new_session = sessions[int(session_id)]["user"] = data.decode(errors="ignore").strip()
				self.local_storage.update(int(session_id), new_session)		
									
		if session['type'] == 'ssh':
			if session['user'] == '':
				handler = session['handler']
				ssh_stdin, ssh_stdout, ssh_stderr = handler.exec_command("whoami", timeout=5, get_pty=True)
				data = ssh_stdout.read() + ssh_stderr.read()
				new_session = sessions[int(session_id)]["user"] = data.decode(errors="ignore").strip()
				self.local_storage.update(int(session_id), new_session)					

		if session['type'] == 'tty':
			if session['user'] == '':
				whoami = self.execute(session_id,"whoami")
				new_session = sessions[int(session_id)]["user"] = whoami
				self.local_storage.update(int(session_id), new_session)		
    
			if session['os'] == '':
				os = self.execute(session_id, "uname")
				new_session = sessions[int(session_id)]["os"] = os
				self.local_storage.update(int(session_id), new_session)

			if session['platform'] == 'Unknow':
				platform = self.execute(session_id, "uname -m")
				new_session = sessions[int(session_id)]["platform"] = platform
				self.local_storage.update(int(session_id), new_session)

			if session['version'] == '':
				version = self.execute(session_id, "lsb_release -a")
				result = ""
				if version:
					v=re.findall(r"Description: (.*) Release", version)
					if v:
						result = v[0]
				new_session = sessions[int(session_id)]["version"] = result
				self.local_storage.update(int(session_id), new_session)
   
	def delete_web_session(self, sid):
		sessions = self.local_storage.get("sessions")
		for i in sessions.keys():
			if sessions[i]['handler'] == sid:
				del sessions[i]
				break
			
class MyHandler_(BaseHTTPRequestHandler):

	def do_GET(self):
		""" Handle GET requests	"""
		command = input("Shell> ")
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(command.encode())
