import os

SECRET_KEY = os.environ.get("SECRET_KEY", "taboo-embedded-dev-secret")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "taboo_cards.csv")
BOT_CLUES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bot_clues.csv")
MAX_PLAYERS_PER_ROOM = 50
CARDS_PER_PLAYER = 4
DEBUG_MODE = True
