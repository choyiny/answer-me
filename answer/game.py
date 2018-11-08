from flask_socketio import Namespace, emit


class Game(Namespace):
    def on_connect(self):
        print("connected")

    def on_disconnect(self):
        print("disconnected")

    def on_my_event(self, data):
        print(data)
        emit('my_response', data)
