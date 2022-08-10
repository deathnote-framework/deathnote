from lib.http.http_client import Http_client
from core.base.option import OptString
from core.utils.printer import *

class Wordpress(Http_client):
    
    wp_user = OptString("admin", "wordpress user", "no")
    wp_password = OptString("admin", "wordpress password", "no")
    
    def wp_login(self):
        
        if not self.wp_user and not self.wp_password:
            print_error("Must have wp_user or wp_password option")
            return
        
        data = {"log": self.wp_user,
                "pwd": self.wp_password,
                "wp-submit": "Log In",
                "redirect_to": self.target+self.uripath+"wp-admin",
                "testcookie":1}
        
        r = self.http_request(
                        method="POST",
                        path="/wp-login.php",
                        data=data,
                        session=True
        )
        if r.status_code == 200:
            return True
        return False       
