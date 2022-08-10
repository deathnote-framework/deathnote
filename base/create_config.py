import string
import random
import os

def random_text(length: int, alph: str = string.ascii_letters + string.digits):
	return "".join(random.choice(alph) for _ in range(length))
	
def create_config_file():

	if not os.path.exists("config"):
		os.mkdir("config")

	config_content = f"""
[FRAMEWORK]
token = None
prompt = deathnote
load_modules_before_start = True
reset_workspace_before_start = True

[API]
user = deathnote
password = {random_text(10)}

[TOR]
enable = False
host = 127.0.0.1
port = 9050

[WEB]
cookie = None
user-agent = Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36

[REMOTESCAN]
user = anonymous
password = anonymous
"""
	with open("config/config.ini", "a") as f:
		f.write(config_content)
		
