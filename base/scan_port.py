import nmap
from core.utils.db import *
from core.utils.printer import *

class Scanner:
	
	def __init__(self, target="127.0.0.1", port="20-1024", workspace="default"):
		self.target = target
		self.port = port
		self.nm = nmap.PortScanner()
		self.workspace = workspace
		check = db.query(Workspace_data).filter(Workspace_data.name==self.workspace, 
												Workspace_data.target==True, 
												Workspace_data.ip==self.target).first()
		if not check:
			add_target = Workspace_data(name=self.workspace, 
										target=True, 
										ip=self.target)
			db.add(add_target)
			db.commit()
	
	def scan(self):

		self.nm.scan(self.target, self.port)

		for host in self.nm.all_hosts():
			print_info('\tHost : {} ({})'.format(host, self.nm[host].hostname()))
			print_info('\tState : {}'.format(self.nm[host].state()))
			for proto in self.nm[host].all_protocols():
				print_info('\t----------')
				print_info('\tProtocol : {}'.format(proto))
		 
				lport = self.nm[host][proto].keys()
				for port in lport:
					print_info('\tport : {}\tstate : {}'.format(port, self.nm[host][proto][port]['state']))
					check = db.query(Workspace_data).filter(Workspace_data.name==self.workspace, 
															Workspace_data.target==False, 
															Workspace_data.ip==self.target, 
															Workspace_data.port==port).first()
					if not check:	
						add_port = Workspace_data(name=self.workspace, target=False, ip=self.target, port=port)
						db.add(add_port)
						db.commit()
