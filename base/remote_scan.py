import threading
import time
from itertools import chain
from core.utils.function import pythonize_path
from core.utils.import_module import import_exploit
from core.utils.locked_iterator import LockedIterator
from core.jobs import Jobs
from core.storage import LocalStorage
from core.utils.db import *
from base.port import port_list, same_module
from base.scan_port import Scanner
import requests

class RemoteScan:

	def __init__(self, target, threads_number, workspace):
		self.target = target
		self.compteur = 0
		self.total = 0
		self.all_modules = []
		self.jobs = Jobs()
		self.job_id = None
		self.local_storage = LocalStorage()
		self.scan_id = None
		self.threads_number = threads_number
		self.port = []
		self.cache = None
		self.protocols = []
		self.port_temporaire = {}
		self.port_scanned = []
		self.workspace = workspace
		self.protocols_ssl = []
	
	def scan_target(self):
		scan = Scanner(target=self.target, port="20-1024", workspace=self.workspace)
		scan.scan()		
		my_target_port = db.query(Workspace_data.port).filter(Workspace_data.name==self.workspace, Workspace_data.ip==self.target, Workspace_data.target==False).all()
		self.port_scanned = [value for value, in my_target_port]
		for port in self.port_scanned:
			try:
				proto = port_list[int(port)]
				self.protocols.append(proto)
				if proto == 'http' or proto == 'https':
					self.cache = requests.get(url=f"{proto}://{self.target}")
				self.port_temporaire[port] = proto
			except:
				continue
		
	def personnalize(self):
		for port in self.port_temporaire:
			proto = self.port_temporaire[port]
			self.protocols.append(proto)
		
	def get_all_modules(self):
		modules_query = db.query(Modules.path).filter(Modules.type_module=='remotescan').all()
		for p in self.protocols:
			if p in same_module:
				p = same_module[p]
				self.protocols_ssl.append(p)
		for value in modules_query:				
			if value[0].split('/')[1] in self.protocols:
				self.all_modules.append(value[0].split('/')[1]+"@@"+value[0])
			if value[0].split('/')[1] in self.protocols_ssl:
				self.all_modules.append(value[0].split('/')[1]+"s@@"+value[0])
		
		return len(self.all_modules)
		
	def run_threads(self, threads_number , target_function , *args, **kwargs):
		threads = []
		threads_running = threading.Event()
		threads_running.set()

		for thread_id in range(int(threads_number)):
			thread = threading.Thread(
				target=target_function,
				args=chain((threads_running,), args),
				kwargs=kwargs,
				name="thread-{}".format(thread_id),
			)
			threads.append(thread)
			thread.start()

		try:
			while thread.is_alive():
				thread.join(1)

		except KeyboardInterrupt:
			threads_running.clear()

		for thread in threads:
			thread.join()
		self.local_storage.delete_element("jobs", self.job_id)
		end = time.time()
		update_status = db.query(Remotescan).filter(Remotescan.id==self.scan_id).first()
		update_status.status = "Finish"
		db.commit()
		
	def load_module(self, running, data):
		while running.is_set():
			new_module = data.next()
			if new_module == False:				
				break
			else:
				proto_of_module = new_module.split("@@")[0]
				module = new_module.split("@@")[1]
				for i in self.port_temporaire.keys():
					if self.port_temporaire[i] == proto_of_module:
						port = i
						break
				module_path = pythonize_path(module)
				module_path = ".".join(("modules",module_path))
				if proto_of_module in same_module:					
					current_module_scan = import_exploit(module_path)(self.target, port, self.cache, True)
				else:
					current_module_scan = import_exploit(module_path)(self.target, port, self.cache)
				try:
					r = current_module_scan.run()
					if r:
						info_return = ""
						if isinstance(r,str):
							info_return = r
						info = current_module_scan.__info__
						add_info = Remotescan_data(remotescan_id=self.scan_id, 
													target=self.target, 
													port=port, 
													cvss3=info['status'], 
													nom=info['description'], 
													cve=info['cve'], 
													modules=info['module'], 
													info=info_return)
						db.add(add_info)
						db.flush()
				except:
					continue
			self.compteur += 1
		db.commit()

	def run(self):
		add_scan = Remotescan(workspace=self.workspace, target=self.target, status="In working...")
		db.add(add_scan)
		db.commit()
		self.scan_id = add_scan.id
		self.job_id = self.jobs.create_job("Remote scan", self.target, self.attack)

	def attack(self):
		self.total = len(self.all_modules)
		data = LockedIterator(self.all_modules)
		self.run_threads(self.threads_number, self.load_module, data)
