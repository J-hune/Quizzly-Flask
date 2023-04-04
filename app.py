from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from blueprints.api.routes import api
import os
from dotenv import load_dotenv
from events import connect, disconnect, createRoomSequence, askCorrection, nextQuestion, askStopResponses, joinRoom, \
    submitAnswer, createRoomQuestion

load_dotenv()

app = Flask(__name__)
app.register_blueprint(api)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

cors = CORS(
    app, resources={r"/*": {"origins": "http://localhost:8080"}},
    supports_credentials=True
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

socketio = SocketIO(app, cors_allowed_origins="*", logger=True, async_mode='eventlet')

# Events communs aux Enseignants et Etudiants
socketio.on_event('connect', connect)
socketio.on_event('disconnect', disconnect)

# Events Enseignants
socketio.on_event('createRoomSequence', createRoomSequence)
socketio.on_event('createRoomQuestion', createRoomQuestion)
socketio.on_event('nextQuestion', nextQuestion)
socketio.on_event('askCorrection', askCorrection)
socketio.on_event('askStopResponses', askStopResponses)

# Events Etudiants
socketio.on_event('joinRoom', joinRoom)
socketio.on_event('submitAnswer', submitAnswer)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
