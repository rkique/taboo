import uuid
import random
import time
from names import generate_name

_rooms = {}

PLAYER_COLORS = [
    "#e74c3c",  # red
    "#3498db",  # blue
    "#2ecc71",  # green
    "#f39c12",  # orange
    "#9b59b6",  # purple
    "#1abc9c",  # teal
    "#e67e22",  # dark orange
    "#e84393",  # pink
]


def create_room(leader_sid):
    """Create a new room and return (room_id, room)."""
    room_id = str(random.randint(1000, 9999))
    room = {
        "leader_sid": leader_sid,
        "players": {leader_sid: {"id": 1, "name": generate_name()}},
        "state": "lobby",  # lobby | clue_phase | guess_phase
        "next_player_id": 2,
        "player_cards": {},      # {sid: [card, ...]}
        "canvas_cards": [],      # [{card_id, card, owner_sid}, ...]
        "player_colors": {},     # {sid: color_hex}
        "player_order": [],      # [sid, ...] in join order for circle layout
        "all_words": [],
        "clues": {},             # {sid: {card_id: clue_text}}
        "card_claims": {},       # {card_id: {claimer_sid, claimer_color}}
        "correct_counts": {},    # {sid: int}
    }
    _rooms[room_id] = room
    return room_id, room


def get_room(room_id):
    return _rooms.get(room_id)


def delete_room(room_id):
    _rooms.pop(room_id, None)


def add_player(room_id, sid):
    """Add a player to a room. Returns (player_info, error_message)."""
    room = get_room(room_id)
    if not room:
        return None, "Room not found."
    if room["state"] != "lobby":
        return None, "Game already in progress."
    if len(room["players"]) >= 50:
        return None, "Room is full (max 50 players)."

    player_id = room["next_player_id"]
    room["next_player_id"] += 1
    info = {"id": player_id, "name": generate_name()}
    room["players"][sid] = info
    return info, None


def rename_player(room_id, sid, new_name):
    room = get_room(room_id)
    if not room or sid not in room["players"]:
        return False
    room["players"][sid]["name"] = new_name
    return True


def remove_player(sid):
    """Remove a player from whatever room they're in.
    Returns (room_id, room) if found, else (None, None).
    """
    for room_id, room in list(_rooms.items()):
        if sid in room["players"]:
            del room["players"][sid]
            if len(room["players"]) == 0:
                del _rooms[room_id]
                return room_id, None
            return room_id, room
    return None, None


def init_game(room_id):
    """Initialize game state: colors, order, empty canvas. Cards added as clues come in."""
    room = get_room(room_id)
    sids = list(room["players"].keys())

    room["player_cards"] = {}
    room["canvas_cards"] = []
    room["player_order"] = sids[:]
    room["player_colors"] = {}
    room["correct_counts"] = {sid: 0 for sid in sids}
    room["card_claims"] = {}
    room["clue_counter"] = {}  # {sid: int} for generating card_ids

    for i, sid in enumerate(sids):
        room["player_colors"][sid] = PLAYER_COLORS[i % len(PLAYER_COLORS)]


def add_clued_card(room_id, sid, card, clue_text):
    """Add a card to the canvas when a player submits a clue. Returns card_id."""
    room = get_room(room_id)
    if not room:
        return None
    count = room["clue_counter"].get(sid, 0)
    card_id = f"{sid}_{count}"
    room["clue_counter"][sid] = count + 1

    room["canvas_cards"].append({
        "card_id": card_id,
        "card": card,
        "owner_sid": sid,
    })

    if sid not in room["clues"]:
        room["clues"][sid] = {}
    room["clues"][sid][card_id] = clue_text

    return card_id



def check_canvas_guess(room_id, sid, card_id, guess_text):
    """Check a guess against the target word. Returns (is_correct, scores_dict).
    If correct, records the claim. Does not store wrong guesses.
    Scoring: 100 pts to guesser, plus owner bonus based on time elapsed.
    """
    room = get_room(room_id)
    if not room:
        return False, {}

    # Find the target card
    target_card = None
    for cc in room["canvas_cards"]:
        if cc["card_id"] == card_id:
            target_card = cc
            break
    if not target_card:
        return False, {}

    target_word = target_card["card"]["word"]
    is_correct = guess_text.lower().strip() == target_word.lower().strip()

    if is_correct:
        room["card_claims"][card_id] = {
            "claimer_sid": sid,
            "claimer_color": room["player_colors"].get(sid, "#888"),
        }

        # 100 pts for guessing correctly
        room["correct_counts"][sid] = room["correct_counts"].get(sid, 0) + 100

        # Owner bonus based on time since guess phase started
        owner_sid = target_card["owner_sid"]
        elapsed = time.time() - room.get("guess_phase_start", time.time())
        if elapsed <= 5:
            bonus = 100
        elif elapsed <= 15:
            bonus = 50
        else:
            bonus = 25
        room["correct_counts"][owner_sid] = room["correct_counts"].get(owner_sid, 0) + bonus

    return is_correct, dict(room["correct_counts"])


def add_bots(room_id, count):
    """Add bot players to a room. Returns list of bot sids."""
    room = get_room(room_id)
    if not room:
        return []
    count = max(0, min(count, 5))
    bot_sids = []
    for i in range(count):
        bot_sid = f"bot_{room_id}_{i}"
        player_id = room["next_player_id"]
        room["next_player_id"] += 1
        room["players"][bot_sid] = {
            "id": player_id,
            "name": f"Bot {i + 1}",
            "is_bot": True,
        }
        if "bots" not in room:
            room["bots"] = []
        room["bots"].append(bot_sid)
        bot_sids.append(bot_sid)
    return bot_sids


def player_list(room_id):
    room = get_room(room_id)
    return list(room["players"].values()) if room else []
