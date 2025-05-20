from flask import Flask
from flask_socketio import SocketIO, send
from flask_cors import CORS
import eventlet

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow CORS for Socket.IO


# count = 0


# def send_count():
#     global count
#     while True:
#         count += 1
#         socketio.emit('count_message', {'count': count})
#         eventlet.sleep(3)


# # @socketio.on('message')
# # def handle_message(msg):
# #     print('Received message: ' + msg)
# #     send(msg, broadcast=True)


# @app.route('/')
# def index():
#     return "Welcome to Flask WebSocket Example!"


# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     socketio.start_background_task(send_count)


# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

count = 0
counting = False  # Flag to control background task
flag = True

def send_count():
    global count, counting
    counting = True
    while counting:
        count += 1
        socketio.emit('count_message', {'count': count})
        eventlet.sleep(4)


def reset_count():
    global count, counting
    counting = False  # Stop the loop
    count = 0
    socketio.emit('reset_count', {'count': 0})


@socketio.on('count_message')
def start_counting(data=None):
    global counting
    if not counting:  # Prevent multiple background tasks
        socketio.start_background_task(send_count)


@socketio.on('reset_count')
def stop_counting():
    reset_count()


@app.route('/')
def index():
    return "Welcome to Flask WebSocket Example!"


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5001)
