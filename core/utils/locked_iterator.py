import threading

class LockedIterator(object):
	def __init__(self, it):
		self.lock = threading.Lock()
		self.it = it.__iter__()

	def __iter__(self):
		return self

	def next(self):
		self.lock.acquire()
		try:
			item = next(self.it)
			return item		
		except StopIteration:
			return False
		finally:
			self.lock.release()	
