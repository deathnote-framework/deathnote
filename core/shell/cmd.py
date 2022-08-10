from core.shell.base_shell import Base_shell
from core.utils.printer import *
from core.utils.db import *
from core.utils.function import pythonize_path
import importlib

class Cmd(Base_shell):
    
    def interactive(self):
        post_modules = db.query(Modules.path, Modules.description).filter(Modules.type_module=="post", Modules.platform==self.platform).all()
        while True:
            command = input(f"({self.platform}:cmd){self.host} > ")
            if not command:
                continue
            elif command == 'exit':
                break
            elif command == 'help':
                print_info()
                print_info('\tHelp command')
                print_info('\t------------')
                print_info('\tpost              show post modules available')
                print_info('\trun <post path>   run post module')
                print_info('\texit              quit the shell')
                print_info()
            elif command == 'post':
                if post_modules:
                    headers= ['path', 'description']
                    print_table(headers, *post_modules, max_column_length=100)
                else:
                    print_info("No post module found")
            elif command.startswith("run "):
                c = command.split(" ")
                if len(c) >= 2:
                    prepare_post = pythonize_path(c[1])
                else:
                    continue
                try:
                    test = getattr(importlib.import_module("modules."+prepare_post), "Module")()
                    setattr(test, 'session', int(self.session_id))
                    test.exploit()
                except:
                    print_error("Problem with post module")
                
            else:
                output = self.sock(command)
                print_info(output)
    
    def execute(self, cmd, raw=False):
        output = self.sock(cmd)
        return output