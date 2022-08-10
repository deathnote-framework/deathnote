from core.shell.base_shell import Base_shell
from core.utils.printer import *

class Shell_subprocess(Base_shell):
    
    def interactive(self):
        while True:
            cmd = input(f"({color_green('pseudo shell')}){self.host}> ")
            if cmd == "back":
                break
            elif cmd == "exit":
                print_status("Hint: If you want just detach the active shell, write: back")
                confirm = input("Are you sure to exit session (y/n) ? ")
                if confirm == "y":
                    self.close()
                    break
            else:
                self.sock.send(cmd)
                d = b""
                while True:
                    data = self.sock.recv(1024)
                    d += data
                    if len(data) < 1024:
                        break
                print_info(d.decode(errors="ignore"))
            
    def execute(self, cmd, raw=False):
        self.sock.send(cmd)
        d = b""
        while True:
            data = self.sock.recv(1024)
            d += data
            if len(data) < 1024:
                break
        return d.decode(errors="ignore")
    
    def close(self):
        self.sock.close()
        del self.sessions[int(self.session_id)]
