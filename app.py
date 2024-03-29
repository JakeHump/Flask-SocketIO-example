#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('join', namespace='/test')
def join(message):
	join_room(message['room'])
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response',
		{'data': 'In rooms: ' + ', '.join(rooms()),
		'count': session['receive_count']})
	print(f"Join emission received from client. Emitting my_response: 'Received: #{session['receive_count']}: In rooms: {rooms()}'")

@socketio.on('leave', namespace='/test')
def leave(message):
	leave_room(message['room'])
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response',
		{'data': 'In rooms: ' + ', '.join(rooms()),
		'count': session['receive_count']})
	print(f"Leave emission received from client. Emitting my_response: 'Received: #{session['receive_count']}: In rooms: {rooms()}'")


@socketio.on('close_room', namespace='/test')
def close(message):
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
						'count': session['receive_count']},
		room=message['room'])
	close_room(message['room'])
	print(f"Close room emission received from client. Emitting my_response: 'Received: #{session['receive_count']}: Room {message['room']} is closing.' Only users in Room {message['room']} can see this message")


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response',
		{'data': message['data'], 'count': session['receive_count']},
		room=message['room'])
	print(f"My room event emission received from client. Emitting my_response: 'Received: #{session['receive_count']}: {message['data']}' to Room {message['room']}. Only users in Room {message['room']} can see this message")

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response',
		{'data': 'Disconnected!', 'count': session['receive_count']})
	disconnect()
	print(f"Disconnect request received from client. Emitting my_response: 'Received: #{session['receive_count']}: Disconnected!'")

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
	print('Client disconnected', request.sid)


if __name__ == '__main__':
	socketio.run(app, debug=True)
