from flask import Flask
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('authenticate')
def handle_authentication(data):
    uid = data.get('uid')
    if uid in users:
        join_room(uid)
        emit('authenticated', {'uid': uid})
    else:
        emit('unauthorized')

if __name__ == '__main__':
    socketio.run(app, host = "0.0.0.0", port=5003, debug=True, allow_unsafe_werkzeug=True)
