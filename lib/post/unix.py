from lib.post.file import File
from core.utils.printer import *

class Unix(File):

	def user_exists(self, user):

		etc_passwd = ["/etc/passwd","/etc/security/passwd","/etc/master.passwd"]
		for i in etc_passwd:
			etc_file = self.read_file(i)
			if user in etc_file:
				return True
		print_error("User doesn't exist")
		return False
		
