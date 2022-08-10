import threading
import ctypes
from core.storage import LocalStorage
from core.utils.printer import *

class Jobs:
	
	def __init__(self):
		
		self.local_storage = LocalStorage()
		self.job_process = None
	
	def start_job(self, job_function, job_arguments):
		self.job_process = threading.Thread(target=job_function, args=job_arguments)
		self.job_process.setDaemon(True)
		self.job_process.start()
	
	def stop_job(self, job):
		if job.is_alive():
			exc = ctypes.py_object(SystemExit)
			res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(job.ident), exc)
			if res == 0:
				raise self.exceptions.GlobalException
			if res > 1:
				ctypes.pythonapi.PyThreadState_SetAsyncExc(job.ident, None)
				raise self.exceptions.GlobalException	
	
	def create_job(self, job_name, module_name, job_function, job_arguments=[]):
		self.start_job(job_function, job_arguments)
		if not self.local_storage.get("jobs"):
			self.local_storage.set("jobs", dict())
		job_id = len(self.local_storage.get("jobs"))
		job_data = {
			job_id: {
				'job_name': job_name,
				'module_name': module_name,
				'job_process': self.job_process
			}
		}
		self.local_storage.update("jobs", job_data)
		return job_id

	def delete_job(self, job_id):
		if self.local_storage.get("jobs"):
			job_id = int(job_id)
			if job_id in list(self.local_storage.get("jobs").keys()):
				try:
					self.stop_job(self.local_storage.get("jobs")[job_id]['job_process'])
					self.local_storage.delete_element("jobs", job_id)
				except Exception:
					print_error("Failed to stop job!")
			else:
				print_error("Invalid job id!")
		else:
			print_error("Invalid job id!")

	def exist_jobs(self):
		jobs = self.local_storage.get("jobs")
		if jobs:
			print_success("Stopping all jobs...")
			for job_id in list(jobs.keys()):
				self.delete_job(job_id)
