from flask import Flask, request
from flask_socketio import SocketIO, join_room, disconnect
from flask_cors import CORS
import eventlet
import uuid
import jwt
import time


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
SECRET_KEY = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

count = 0
counting = False  # Flag to control background task


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


def generate_channel_token(channel_id):
    payload = {
        'channel_id': channel_id,
        'exp': int(time.time()) + 600  # Token valid for 10 minutes
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


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


@app.route('/api/get-channel-token/', methods=['GET'])
def generateChannelID():
    user_id = uuid.uuid4()
    channel_id = f"user_{user_id}"
    token = generate_channel_token(channel_id)
    return {"channel_id": channel_id, "token": token}


@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')

    if not token or not channel_id:
        print("Missing token or channel_id")
        disconnect()
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload['channel_id'] != channel_id:
            print("Channel mismatch")
            disconnect()
            return

        # Passed validation
        join_room(channel_id)
        print(f"Client connected and joined channel {channel_id}")

    except jwt.ExpiredSignatureError:
        print("Token expired")
        disconnect()
    except jwt.InvalidTokenError:
        print("Invalid token")
        disconnect()


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5001)
