import os

SECRET_KEY = os.environ.get("SECRET_KEY", "taboo-embedded-dev-secret")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "blather_round_taboo.csv")
BOT_CLUES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bot_clues.csv")
MAX_PLAYERS_PER_ROOM = 50
DEBUG_MODE = True
CLUE_PHASE_TIME = 60        # seconds for the entire clue phase
GUESS_PHASE_TIME = 60       # seconds for the entire guess phase
