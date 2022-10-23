from flask import Flask, render_template, current_app
from flask_socketio import SocketIO
from servos import Servo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spooooooky'
socketio = SocketIO(app)

# Set up our servos, offset by -20 to account for where it was installed
horizontalservo = Servo(23, offset=-20)
verticalservo = Servo(27)

@socketio.on('faceposition')
def handle_message(data):
    # Move eyes
    horizontalservo.set_fraction((data[2]-data[0])/data[2], minimum=-45, maximum=30)
    verticalservo.set_fraction(data[1]/data[3], minimum=-45, maximum=45)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
