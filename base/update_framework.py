import subprocess
from base.version import __version__
from base.config import DeathnoteConfig
from core.utils.printer import print_error, print_success

class Update_framework:
    
    def __init__(self):
        self.my_config = DeathnoteConfig()
        self.token = self.my_config.get_config('FRAMEWORK','token')
    
    def update(self):
        """ Update """
        if self.token == "None":
            print_error("No token found in config/config.ini")
            return
        print_success("Update deathnote...")
        try:
            subprocess.call(['git','pull', f'https://oauth2:{self.token}@deathnote-framework.io:8765/main/deathnote.git'])
            print_status("Framework must be restart for run updated core")
            print_success('Update success!')
        except:
            print_error('Update failed!')
            print_error('Token not valid')