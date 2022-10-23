from flask import Flask, render_template, current_app
from flask_socketio import SocketIO
from servos import Servo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spooooooky'
socketio = SocketIO(app)

# Set up our servos
horizontalservo = Servo(23)
verticalservo = Servo(27)

@socketio.on('faceposition')
def handle_message(data):
    print(f'face: x={data[0]} y={data[1]}')

    # Move eyes
    horizontalservo.set_fraction(-data[0]/640)
    verticalservo.set_fraction(data[1]/480)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
