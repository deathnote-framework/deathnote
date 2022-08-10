from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.completion import Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import ANSI
from base.config import DeathnoteConfig
from base.exceptions import DeathnoteException
from core.all_commands import All_commands
from core.utils.printer import *
from core.utils.db import *
from core.utils.function import *
from core.sessions import Sessions
from core.commands import GLOBAL_COMMANDS, SUB_COMMANDS
from core.utils.db import db, Workspace
import os

class Base:


	def available_modules_completion(self, text):
		""" Looking for tab completion hints using setup.py entry_points.

		May need optimization in the future!

		:param text: argument of 'use' command
		:return: list of tab completion hints
		"""
		all_possible_matches = filter(lambda x: x.startswith(text), self.modules)
		matches = set()
		for match in all_possible_matches:
			head, sep, tail = match[len(text):].partition('.')
			if not tail:
				sep = ""
			matches.add("".join((text, head, sep)))
		return list(map(humanize_path, matches))

	def complete_use(self, text, *args, **kwargs):
		if text:
			return self.available_modules_completion(text)
		else:
			return self.modules

	def complete_doc(self, text, *args, **kwargs):

		libs = []
		for root, dirs, files in os.walk("lib"):
			_, package, root = root.rpartition("lib/".replace("/", os.sep))
			root = root.replace(os.sep, ".")
			files = filter(lambda x: not x.startswith("__") and x.endswith(".py"), files)
			if root == "lib":
				libs.extend(map(lambda x: "".join(("", os.path.splitext(x)[0])), files))
			else:
				libs.extend(map(lambda x: ".".join((root, os.path.splitext(x)[0])), files))
				
		if text:
			return [lib for lib in libs if lib.startswith(text)]
		else:
			return libs

	def complete_show(self, text, *args, **kwargs):
		if text:
			return [command for command in SUB_COMMANDS if command.startswith(text)]
		else:
			return SUB_COMMANDS

	def complete_set(self, text, *args, **kwargs):
		if text:
			if text.startswith('payload') or text.startswith('ppayload'):
				if 'ppayload' in text:
					text = text.replace('ppayload ', 'payload ')
				prefix = text[:7]
				text = text[7:]
				return [f"{prefix}".join((p, ""))for p in self.commands.list_available_payload if p.startswith(text)]
			return ["".join((attr, "")) for attr in self.commands.current_module.options if attr.startswith(text)]

		else:

			return self.commands.current_module.options
	
	def complete_load(self, text, *args, **kwargs):
		
		ressources = []
		for root, dirs, files in os.walk("scripts"):
			_, package, root = root.rpartition("scripts/".replace("/", os.sep))
			root = root.replace(os.sep, ".")			
			files = filter(lambda x: not x.startswith("__") and x.endswith(".sc"), files)
			ressources.extend(map(lambda x: "".join(("", x)), files))
			
		if text:
			return [ressource for ressource in ressources if ressource.startswith(text)]
		else:
			return ressources

class Interpreter(Base):

	
	def __init__(self):
		super(Interpreter, self).__init__()
		self.my_config = DeathnoteConfig()
		self.commands = All_commands()
		self.current_module = None
		self.loading = 0
		self.modules = index_modules()
		self.session = Sessions()
		if not os.path.exists("log"):
			os.mkdir("log")
		self.history = FileHistory("log/log_history")
		if self.my_config.get_config('FRAMEWORK', 'reset_workspace_before_start') == "True":
			init_default = db.query(Workspace).filter(Workspace.name == "default").all()
			for i in init_default:
				db.delete(i)
			db.commit()
			default = Workspace("default")
			db.add(default)
			db.commit()				

	def prompt(self):
		my_prompt = self.my_config.get_config('FRAMEWORK','prompt')
		self.commands.auto_attack_run_background()
		get_len_session = len(self.session.get_all_sessions().keys())
		if self.commands.current_module:	
			my_prompt += "("+color_green(self.commands.module_metadata['name'])+")"
		my_prompt = f"[{color_green(get_len_session)}]{my_prompt} > "
		return ANSI(my_prompt)

	def get_completions(self, document, complete_event):
		self.loading += 1
		text = document.text
		word_before_cursor = document.get_word_before_cursor()
		try:
			if text:
				try:
					cmd, args, _ = parse_command_line(text)
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
		
	def start(self):

		self.commands.get_plugins()
		self.commands.command_clear()
		if self.my_config.get_config('FRAMEWORK','load_modules_before_start') == "True":
			self.commands.command_db_reload_all()
			self.modules = index_modules()
   
		self.commands.slow_start()
		print_info()
		while True:
			try:
				my_command = prompt(self.prompt,
									history=self.history,
									completer=self,
									complete_in_thread=True,
									complete_while_typing=True,
									complete_style=CompleteStyle.READLINE_LIKE,
									refresh_interval=0.5)
				command, args, kwargs = parse_command_line(my_command)
				command = command.lower()
				if not command:
					continue
				if command in self.commands.plugins:
					try:
						load_plugin = __import__('plugins.{}'.format(command), fromlist=['Module'])
						plugin = getattr(load_plugin, 'Module')()
						plugin.run(args, **kwargs)	
					except SyntaxError as e:
						print_error(e)					
				else:
					command_handler = self.commands.get_command_handler(command)
					command_handler(args, **kwargs)
					if command == "db_reload":
						self.modules = index_modules()

			except DeathnoteException as err:
				print_error(err)
			except (EOFError, SystemExit):
				break
			except NameError as e:
				print_error(e)
			except KeyboardInterrupt:
				print_error("Interrupt: use the 'exit' command to quit")
			except FileNotFoundError as e:
				print_error(e)
			except:
				print_error("Error")
