from flask import Flask, render_template, current_app
from flask_socketio import SocketIO
from servos import Servo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spooooooky'
socketio = SocketIO(app)

# Set up our servos, offset by -20 to account for where it was installed
horizontalservo = Servo(23, offset=-20)
verticalservo = Servo(27)
lidservo = Servo(17)

@socketio.on('faceposition')
def handle_message(data):
    #message format is [current x, current y, max x, max y, lidposition].
    current_X = data[0]
    current_Y = data[1]
    max_X = data[2]
    max_Y = data[3]
    lidposition = data[4]

    # Move eyes
    horizontalservo.set_fraction((max_X-current_X)/max_X, minimum=-45, maximum=30)
    verticalservo.set_fraction(current_Y/max_Y, minimum=-45, maximum=45)
    # Open=-60, closed=20
    lidservo.set_fraction(lidposition, minimum=-60, maximum=20)

if __name__ == '__main__':
    # Bind to all addresses, allow to start via systemd
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True)
