from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import config
import rooms
from cards import load_cards
import events

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
#Allow CORS from all origins
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

CARDS = load_cards()
print(f"Loaded {len(CARDS)} taboo cards.")

events.register(socketio)


@app.route("/")
def index():
    return jsonify({"status": "ok", "rooms": len(rooms.all_rooms_summary())})

#Display all rooms. 
@app.route("/api/rooms")
def list_rooms():
    return jsonify(rooms.all_rooms_summary())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
