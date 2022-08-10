from core.shell.base_shell import Base_shell
from core.utils.printer import *
import select
import uuid
import re

class Tty(Base_shell):
    
    def interactive(self):
        running = True
        while running:
            socket_list = [sys.stdin, self.sock]

            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                if sock == s:
                    data = sock.recv(4096)
                    sys.stdout.write(data.decode())
                    sys.stdout.flush()
            
                else:
                    message = os.read(sys.stdin.fileno(), 10240)
                    if message.decode().strip() == "back":
                        running = False
                        break
                    elif message.decode().strip() == "exit":
                        print_status("Hint: If you want just detach the active shell, write: back")
                        confirm = input("Are you sure to exit session (y/n) ? ")
                        if confirm == "y":	
                            self.sock.close()
                            self.delete_session(self.session_id)
                            running = False
                            break
                        else:
                            message = b"\n"
                    self.sock.send(message)
    
    def execute(self, cmd, raw=False):
        if not raw: 
            token = str(uuid.uuid4())
            cmd = f"export DELIMITER={token}; echo $DELIMITER$({cmd})$DELIMITER\n".encode()
            self.sock.send(cmd)
            d = b""
            while True:
                data = self.sock.recv(1024)
                d += data
                if len(data) < 1024:
                    if token in d.decode():
                        break
                    else:
                        self.sock.send('\n'.encode())
            result = re.findall(rf"{token}(.*){token}", d.decode(errors="ignore"))[0]
            return result
        else:
            cmd = cmd+"\n"
            self.sock.send(cmd.encode())
            d = b""
            while True:
                data = self.sock.recv(1024)
                d += data
                if len(data) < 1024:
                    break
            return d.decode(errors="ignore")