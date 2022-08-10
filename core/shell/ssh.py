from core.shell.base_shell import Base_shell
from core.utils.printer import *
import select
import os

class Ssh(Base_shell):
    
    def execute(self, cmd, raw=False):
        ssh_stdin, ssh_stdout, ssh_stderr = self.sock.exec_command(cmd, timeout=5)
        data = ssh_stdout.read() + ssh_stderr.read()
        if data:
            return data.decode(errors="ignore")
        return ""
    
    def interactive(self):
        s = self.sock.invoke_shell()
        stdin = s.makefile('wb')
        stdout = s.makefile('rb')
        if os.name != 'nt':
            running = True
            while running:
                socket_list = [sys.stdin, s]

                read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
                for sock in read_sockets:
                    if sock == s:
                        data = sock.recv(1024)
                        sys.stdout.write(data.decode(errors="ignore"))
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
                                self.close()
                                running = False
                                break
                            else:
                                message = b"\n"
                        s.send(message)
        else:
            try:
                import tendo.ansiterm
            except:
                pass
            import win32api
            import win32console
            import win32event
            import win32file
            sock_event = win32event.CreateEvent(None, True, False, None)
            win32file.WSAEventSelect(s.fileno(), sock_event, win32file.FD_CLOSE | win32file.FD_READ)
            stdin = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
            console = win32console.GetStdHandle(win32api.STD_INPUT_HANDLE)
            handles = [stdin, sock_event]
            buf = ""
            try:
                while True:
                    i = win32event.WaitForMultipleObjects(handles, 0, 1000)
                    if i == win32event.WAIT_TIMEOUT:
                        continue
                    if handles[i] == stdin:
                        rs = console.ReadConsoleInput(1)
                        if rs[0].EventType == win32console.KEY_EVENT and rs[0].KeyDown:
                            if rs[0].VirtualKeyCode == 0x0d:
                                sys.stdout.write("\n")
                                sys.stdout.flush()
                                format_buf = buf + "\n"
                                s.send(format_buf.encode())
                                if buf == "exit":
                                    s.close()
                                    break
                                buf = ""
                            elif rs[0].VirtualKeyCode == 0x08:
                                sys.stdout.write("\b")
                                sys.stdout.write(" ")
                                sys.stdout.write("\b")
                                sys.stdout.flush()
                                buf = buf[:-1]
                            else:
                                c = rs[0].Char
                                if c == "\x00":
                                    continue
                                buf += c
                                sys.stdout.write(c)
                                sys.stdout.flush()
                                
                    if handles[i] == sock_event:
                        while True:
                            data = s.recv(4096)
                            sys.stdout.write(data.decode())
                            if len(data) < 4096:
                                break
                        win32event.ResetEvent(sock_event)
            finally:
                win32api.CloseHandle(sock_event)