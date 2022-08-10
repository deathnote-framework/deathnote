import requests
from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.completion import Completion
from prompt_toolkit.formatted_text import ANSI
import os
import argparse
import base64

GLOBAL_COMMANDS = ['list', 'interact', 'help', 'clear']

def print_table(headers, *args, **kwargs) -> None:

	terminal_columns, terminal_rows = os.get_terminal_size(0)
	extra_fill = kwargs.get("extra_fill", 5)
	header_separator = kwargs.get("header_separator", "-")

	if not all(map(lambda x: len(x) == len(headers), args)):
		print(args)
		print("Headers and table rows tuples should be the same length.")
		return

	def custom_len(x):
		try:
			return len(x)
		except TypeError:
			return 0

	fill = []
	headers_line = '   '
	headers_separator_line = '   '
	for idx, header in enumerate(headers):
		column = [custom_len(arg[idx]) for arg in args]
		column.append(len(header))

		current_line_fill = max(column) + extra_fill
		fill.append(current_line_fill)
		headers_line = "".join((headers_line, "{header:<{fill}}".format(header=header, fill=current_line_fill)))
		headers_separator_line = "".join((
			headers_separator_line,
			"{:<{}}".format(header_separator * len(header), current_line_fill)
		))

	print('\n')
	print(headers_line)
	print(headers_separator_line)
	for arg in args:
		content_line = "   "
		for idx, element in enumerate(arg):
			content_line = "".join((
				content_line,
				"{:<{}}".format(element, fill[idx])
			))
		print(content_line[:terminal_columns])

	print('\n')

class Client_api:

	def __init__(self, ip="127.0.0.1", port=8080, user="admin", password="admin"):
		self.loading = 0
		self.token = ""
		self.ip = ip
		self.port = port
		self.user = user
		self.password = password

	def parse_line(self, line):
		kwargs = dict()
		command, _, arg = line.strip().partition(" ")
		return command, arg.strip(), kwargs

	def get_completions(self, document, complete_event):
		self.loading += 1
		text = document.text
		word_before_cursor = document.get_word_before_cursor()
		try:
			if text:
				try:
					cmd, args, _ = self.parse_line(text)
					complete_function = getattr(self, "complete_"+cmd)(args)# + word_before_cursor
					for i in complete_function:
						yield Completion(i, -len(args))
				except:
					for word in GLOBAL_COMMANDS:
						if word.startswith(word_before_cursor):
							yield Completion(word+" ", -len(word_before_cursor))
			else:
				for word in GLOBAL_COMMANDS:
					if word.startswith(word_before_cursor):
						yield Completion(word+" ", -len(word_before_cursor))

		finally:
			self.loading -= 1	

	def prompt(self):
		return ANSI("session > ")
	
	def authenticate(self):		
		try:
			login = requests.get(f"http://{self.ip}:{self.port}/api/login?username={self.user}&password={self.password}")
		except requests.exceptions.ConnectionError:
			return "[-] Connection error"
		if login:
			access = login.json()
			if access['success'] == True:
				self.token = access['token']
				return True
		return "[-] Authentification failed"
	
	def start(self):
		headers = {"x-access-token": self.token}
		print("")
		print("+ -- --=[ Welcome")
		print("+ -- --=[ Deathnote framework api session client")
		print("+ -- --=[ Type 'help' for more information")
		print("")
		while True:
			command = prompt(self.prompt,
					completer=self,
					complete_in_thread=True,
					complete_while_typing=True,
					complete_style=CompleteStyle.READLINE_LIKE)
			if command == "exit":
				break
			elif command.startswith("help"):
				print("\n")
				print("\thelp menu")
				print("\t---------")
				print("\tlist              show all sessions")
				print("\tinteract <id>     interact with session id")
				print("\tclear             clear screen")
				print("\texit              quit client")
				print("\n")
			elif command.startswith("list"):
				get_sessions = requests.get(f"http://{self.ip}:{self.port}/api/all_sessions", headers=headers, timeout=5)
				if get_sessions:
					all_sessions = get_sessions.json()
					if all_sessions:
						sessions_data = list()
						headers_display = ("Id", "User", "Platform", "Version", "type", "host", "port")
						for session_id in all_sessions.keys():
							session_user = all_sessions[session_id]['user']
							session_platform = all_sessions[session_id]['platform']
							session_version = all_sessions[session_id]['version']
							session_type = all_sessions[session_id]['type']
							host = all_sessions[session_id]['host']
							port = all_sessions[session_id]['port']
							sessions_data.append((session_id, session_user, session_platform, session_version, session_type, host, port))
						print("\n")
						print("Active sessions")
						print_table(headers_display, *sessions_data)
					else:
						print('No active sessions')
			elif command.startswith("clear"):
				if os.name != 'nt':
					os.system('clear')
				else:
					os.system('cls')				
			elif command.startswith("interact"):
				_, id_session = command.split(' ')
				check_if_exist = requests.get(f"http://{self.ip}:{self.port}/api/check_session?id_session={id_session}", headers=headers, timeout=5)
				check = check_if_exist.json()
				if check["success"] == True:
					while True:
						c = input()
						if c == "exit":
							break
						elif c == "help":
							print("\t No help menu")
						else:
							c = base64.b64encode(c.encode('utf-8')).decode()
							try:
								r = requests.get(f"http://{self.ip}:{self.port}/api/session?id_session={id_session}&cmd={c}", headers=headers, timeout=8)
							except requests.exceptions.ConnectionError:
								print("[-] session disconnected")
							if r:
								print(r.json()['data'], end="")		
				else:
					print("[-] id session doesn't exist")


def main():
	""" Api session, interactive """
	parser = argparse.ArgumentParser(description=main.__doc__, prog="client_api")
	parser.add_argument("--host", dest="host", help="host")
	parser.add_argument("--port", dest="port", help="port")
	parser.add_argument("--user", dest="user", help="user")
	parser.add_argument("--password", dest="password", help="password")
	args = parser.parse_args()
	if args is None:
		parser.print_help()
		return	

	if args.host and args.port and args.user and args.password:
		client = Client_api(args.host, args.port, args.user, args.password)
		connected = client.authenticate()
		if connected == True:
			client.start()
		else:
			print(connected)
	else:
		parser.print_help()


if __name__ == "__main__":
	main()

