from core.jobs import Jobs
from core.storage import LocalStorage
from core.utils.db import *
from core.utils.locked_iterator import LockedIterator
from core.utils.function import pythonize_path
from core.utils.import_module import import_exploit
import threading
from itertools import chain
import time

class LocalScan:

	def __init__(self, session, threads_number):
		self.session = session
		self.threads_number = threads_number
		self.jobs = Jobs()
		self.job_id = None		
		self.local_storage = LocalStorage()
		self.target = self.local_storage.get("sessions")[int(self.session)]["host"]
		self.compteur = 0
		self.total = 0
		self.all_modules = []	
		self.protocols = []	

	def get_all_modules(self):
		modules_query = db.query(Modules.path).filter(Modules.type_module=='localscan').all()	
		self.all_modules = [value for value, in modules_query if value.split('/')[1] in self.protocols]	
		return len(self.all_modules)

	def run_threads(self, threads_number , target_function , *args, **kwargs):
		start = time.time()
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
		update_status = db.query(Localscan).filter(Localscan.id==self.scan_id).first()
		update_status.status = "Finish"
		total_time = int(end - start)
		update_status.time = total_time
		db.commit()		

	def load_module(self, running, data):
		while running.is_set():
			new_module = data.next()
			if new_module == False:				
				break
			else:
				module_path = pythonize_path(new_module)
				module_path = ".".join(("modules",module_path))
				current_module_scan = import_exploit(module_path)(self.session)
				r = current_module_scan.run()
				if r:
					info_return = ""
					if isinstance(r,str):
						info_return = r        
					info = current_module_scan.__info__
					add_info = Localscan_data(localscan_id=self.scan_id, 
												target=self.target,  
												cvss3=info['cvss3'], 
												nom=info['name'], 
												cve=info['cve'], 
												modules=info['module'], 
												info=info_return)
					db.add(add_info)
					db.commit()
			self.compteur += 1

	def run(self):
		add_scan = Localscan(workspace="default", target=self.target, status="In working...")
		db.add(add_scan)
		db.commit()
		self.scan_id = add_scan.id
		self.job_id = self.jobs.create_job("Local scan", self.session, self.attack)

	def attack(self):
		self.total = len(self.all_modules)
		data = LockedIterator(self.all_modules)
		self.run_threads(self.threads_number, self.load_module, data)
