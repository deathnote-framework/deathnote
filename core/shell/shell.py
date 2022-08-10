from core.shell.base_shell import Base_shell
from core.utils.printer import *
import os
import select
import sys
import shutil

class Shell(Base_shell):
    
    def interactive(self):
        if os.name != 'nt':
            running = True
            while running:
                socket_list = [sys.stdin, self.sock]

                read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
                for sock in read_sockets:
                    if sock == self.sock:
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
                        self.sock.send(message)
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
    
    def execute(self, cmd, raw=False):

        if self.os == "Windows":
            if not raw:
                self.sock.send(b"echo off\n")
                cmd = cmd+"\n"
                self.sock.send(cmd.encode())
                d = b""
                while True:
                    data = self.sock.recv(1024)
                    d += data
                    if len(data) < 1024:
                        break	
                self.sock.send(b"echo on\n")
                self.sock.recv(1024)
                return d.decode(errors="ignore")

        else:
            c = cmd+'\n'
            self.sock.send(c.encode())
            d = b""
            while True:
                data = self.sock.recv(1024)
                d += data
                if len(data) < 1024:
                    break
            return d.decode(errors="ignore")

    def upgrade(self):
        cmd = "export TERM=xterm-256color; PTY=\"import pty; pty.spawn('/bin/bash')\";{ python3 -c \"$PTY\" || python -c \"$PTY\"; } 2>/dev/null;\n"
        self.sock.send(cmd.encode())
        self.sock.recv(1024)
        terminal_size = shutil.get_terminal_size()
        terminal_columns = terminal_size.columns
        terminal_rows = terminal_size.lines
        self.sock.send(f"stty raw -echo;stty rows {terminal_rows} columns {terminal_columns}\n".encode())
        while True:
            d = s.recv(1024)
            if len(d) < 1024:
                break
        update = self.session_update("type", "tty")
        if update:
            print_success("Shell upgraded: basic shell -> tty")
        else:
            print_error("Shell upgrade failed")
    
    def close(self):
        self.sock.close()
        del self.sessions[int(self.session_id)]