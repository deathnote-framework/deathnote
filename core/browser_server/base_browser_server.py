from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin


import os
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True

app = Flask(__name__, template_folder=os.getcwd()+'/core/browser_server/templates',)
app.config['SECRET_KEY'] = os.urandom(32)
socketio = SocketIO()
socketio.init_app(app, ping_timeout=6, ping_interval=2, async_mode='threading', cors_allowed_origins="*")

