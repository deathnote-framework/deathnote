from core.base.base_module import BaseModule
from core.utils.printer import *
from core.utils.db import *

class Report(BaseModule):
	
	def save_credential(self, host="", username="", password="", data=""):
		"""save credential in database"""
		
		add_creds = Credentials(module_name=self._Module__info__['name'],
								host=host,
								username=username,
								password=password,
								data=data)
		db.add(add_creds)
		db.commit()
