from core.storage import LocalStorage

class Base_shell:
    
    def __init__(self,session_id):
        
        self.local_storage = LocalStorage()
        self.sessions = self.local_storage.get("sessions")
        self.session = self.sessions[int(session_id)]
        self.session_id = int(session_id)
        self.sock = self.session['handler']
        self.host = self.session['host']
        self.os = self.session['os']
        self.platform = self.session['arch']
        self.version = self.session['version']
        self.user = self.session['user']
        self.type = self.session['type']
    
    def interactive(self):
        pass
    
    def execute(self, cmd, raw=False):
        pass
    
    def upgrade(self):
        pass
    
    def close(self):
        pass

    def determinate(self):
        pass

    def session_update(self, key, value):
        try:
            update_session = self.sessions[int(self.session_id)][key] = value
            self.local_storage.update(int(self.session_id), update_session)
            return True
        except:
            return False