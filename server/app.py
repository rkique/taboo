"""
Main Flask application for the Taboo game server.
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import config
import rooms
from cards import load_cards
import events

DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
app.config["SECRET_KEY"] = config.SECRET_KEY
#Allow CORS from all origins
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

CARDS = load_cards()
print(f"Loaded {len(CARDS)} taboo cards.")

events.register(socketio)

#Display all rooms.
@app.route("/api/rooms")
def list_rooms():
    return jsonify(rooms.all_rooms_summary())


@app.route("/")
def index():
    return send_from_directory(DIST_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    if os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
