import socketio
import eventlet
import socket
from time import sleep

sio = socketio.Server(cors_allowed_origins='*')

app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def join_room(sid, room):
    print(f'Client {sid} joined room: {room}')
    sio.enter_room(sid, room)  # Place client in the specified room

@sio.event
def message_from_client(sid, data):
    print('Received message from client:', data)

    # Emitting an event to all clients in the specified room
    sio.emit('message_to_client', data=data)
    


if __name__ == '__main__':
    # Create an eventlet WSGI server (or you can use gevent, asyncio, etc.)
    h_name = socket.gethostname()
    while True:
        IP_addres = socket.gethostbyname(h_name)
        if "127.0.0" not in IP_addres:
            eventlet.wsgi.server(eventlet.listen((IP_addres, 4000)), app)
        else:
            sleep(5)
    
    
