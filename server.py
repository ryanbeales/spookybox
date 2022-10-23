from flask import Flask, render_template, current_app
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# UI files
@app.route('/')
def spookyui():
   return current_app.send_static_file('index.html')

@app.route('/video.js')
def spookyui():
   return current_app.send_static_file('video.js')

@socketio.on('message')
def handle_message(data):
    print('message text: ' + data)

if __name__ == '__main__':
    socketio.run(app)