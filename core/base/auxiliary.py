from core.base.base_module import BaseModule
from core.utils.printer import *
from core.jobs import Jobs
from weakref import WeakKeyDictionary
from itertools import chain
import threading
import time

thread_output_stream = WeakKeyDictionary()

class Auxiliary(BaseModule):

	def __init__(self):
		super(Auxiliary, self).__init__()
		self.job = Jobs()
		self.current_version = 0
		self.type_module = "auxiliary"

	def run(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def check(self):
		raise NotImplementedError("You have to define your own 'run' method.")

	def version(self, argument=None):
		info = self._Module__info__['version']
		if not argument:
			for i,j in enumerate(info.keys()):
				if i == self.current_version:
					return j
		if self.current_version:
			for i,j in enumerate(info.keys()):
				if i == self.current_version:
					return info[j][argument]
		return
	
	def exploit(self):
		self._output.clear()
		self.run()
	
	def run_threads(self, threads_number: int, target_function: any, *args, **kwargs) -> None:
		""" Run function across specified number of threads

		:param int thread_number: number of threads that should be executed
		:param func target_function: function that should be executed accross specified number of threads
		:param any args: args passed to target_function
		:param any kwargs: kwargs passed to target function
		:return None
		"""

		threads = []
		threads_running = threading.Event()
		threads_running.set()

		for thread_id in range(4):#int(threads_number)):
			thread = threading.Thread(
				target=self.toto,#target_function,
				args=[],#chain((threads_running,), args),
				kwargs=kwargs,
				name="thread-{}".format(thread_id),
			)
			threads.append(thread)

			# print_status("{} thread is starting...".format(thread.name))
			thread.start()

		start = time.time()
		try:
			while thread.isAlive():
				thread.join(1)

		except KeyboardInterrupt:
			threads_running.clear()

		for thread in threads:
			thread.join()
			# print_status("{} thread is terminated.".format(thread.name))

		print_status("Elapsed time: {0:.4f} seconds".format(round(time.time() - start, 2)))
