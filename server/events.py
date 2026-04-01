import random
from flask import request
from flask_socketio import join_room, leave_room, emit
import rooms
from config import CARDS_PER_PLAYER, DEBUG_MODE


def register(socketio):
    """Register all SocketIO event handlers."""

    @socketio.on("connect")
    def on_connect():
        print(f"Connected: {request.sid}")

    @socketio.on("disconnect")
    def on_disconnect():
        sid = request.sid
        print(f"Disconnected: {sid}")
        room_id, room = rooms.remove_player(sid)
        if room_id and room:
            leave_room(room_id)
            emit("player_left", {
                "player_count": len(room["players"]),
                "players": rooms.player_list(room_id),
            }, room=room_id)

    @socketio.on("create_room")
    def on_create_room(data):
        sid = request.sid
        room_id, room = rooms.create_room(sid)
        player_info = room["players"][sid]
        join_room(room_id)
        emit("room_created", {
            "room_id": room_id,
            "player_id": player_info["id"],
            "player_name": player_info["name"],
            "is_leader": True,
            "players": rooms.player_list(room_id),
        })

    @socketio.on("join_room")
    def on_join_room(data):
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()

        player_info, error = rooms.add_player(room_id, sid)
        if error:
            emit("error", {"message": error})
            return

        join_room(room_id)
        players = rooms.player_list(room_id)

        emit("room_joined", {
            "room_id": room_id,
            "player_id": player_info["id"],
            "player_name": player_info["name"],
            "is_leader": False,
            "players": players,
        })
        emit("player_joined", {
            "player_count": len(players),
            "players": players,
        }, room=room_id, include_self=False)

    @socketio.on("rename")
    def on_rename(data):
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()
        new_name = data.get("name", "").strip()[:30]

        if not new_name:
            emit("error", {"message": "Name cannot be empty."})
            return

        if rooms.rename_player(room_id, sid, new_name):
            emit("name_updated", {"name": new_name})
            emit("player_joined", {
                "player_count": len(rooms.player_list(room_id)),
                "players": rooms.player_list(room_id),
            }, room=room_id)

    @socketio.on("add_bots")
    def on_add_bots(data):
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()
        count = data.get("count", 0)
        room = rooms.get_room(room_id)

        if not room:
            emit("error", {"message": "Room not found."})
            return
        if room["leader_sid"] != sid:
            emit("error", {"message": "Only the leader can add bots."})
            return

        # Remove existing bots first
        for bot_sid in room.get("bots", []):
            room["players"].pop(bot_sid, None)
        room["bots"] = []

        if count > 0:
            rooms.add_bots(room_id, count)

        emit("player_joined", {
            "player_count": len(room["players"]),
            "players": rooms.player_list(room_id),
        }, room=room_id)

    @socketio.on("start_game")
    def on_start_game(data):
        from app import CARDS
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()
        room = rooms.get_room(room_id)

        if not room:
            emit("error", {"message": "Room not found."})
            return
        if room["leader_sid"] != sid:
            emit("error", {"message": "Only the leader can start the game."})
            return

        num_players = len(room["players"])
        total_needed = CARDS_PER_PLAYER * num_players

        if total_needed > len(CARDS):
            emit("error", {"message": f"Not enough cards. Need {total_needed}, have {len(CARDS)}."})
            return

        rooms.assign_unique_cards(room_id, CARDS, CARDS_PER_PLAYER)
        room["all_words"] = [c["word"] for c in CARDS]
        room["state"] = "clue_phase"
        room["clues"] = {}

        # Auto-submit clues for bots — clue is just the answer word
        bot_sids = room.get("bots", [])
        for bot_sid in bot_sids:
            room["clues"][bot_sid] = {}
            for cc in room["canvas_cards"]:
                if cc["owner_sid"] == bot_sid:
                    room["clues"][bot_sid][cc["card_id"]] = cc["card"]["word"]

        # Send each real player only their own cards
        for player_sid in room["players"]:
            if player_sid in bot_sids:
                continue
            my_cards = []
            for cc in room["canvas_cards"]:
                if cc["owner_sid"] == player_sid:
                    my_cards.append({
                        "card": cc["card"],
                        "card_id": cc["card_id"],
                    })
            socketio.emit("game_started", {
                "cards": my_cards,
                "word_list": room["all_words"],
            }, room=player_sid)

    @socketio.on("submit_clue")
    def on_submit_clue(data):
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()
        card_id = data.get("card_id")
        clue = data.get("clue", "").strip()[:200]

        room = rooms.get_room(room_id)
        if not room or room["state"] != "clue_phase":
            return
        if not clue:
            emit("error", {"message": "Clue cannot be empty."})
            return

        # Check for taboo words and target word in the clue
        target_card = None
        for cc in room["canvas_cards"]:
            if cc["card_id"] == card_id:
                target_card = cc["card"]
                break
        if target_card:
            clue_lower = clue.lower()
            if target_card["word"].lower() in clue_lower:
                emit("error", {"message": f'Your clue cannot contain the target word "{target_card["word"]}".'})
                return
            for tw in target_card["taboo_words"]:
                if tw.lower() in clue_lower:
                    emit("error", {"message": f'Your clue cannot contain the taboo word "{tw}".'})
                    return

        player_done, all_done = rooms.record_clue(room_id, sid, card_id, clue)
        emit("clue_submitted", {"card_id": card_id, "clues_done": player_done})

        # Progress
        all_players = list(room["players"].keys())
        players_fully_done = sum(
            1 for s in all_players
            if all(
                cid in room["clues"].get(s, {})
                for cid in [c["card_id"] for c in room["canvas_cards"] if c["owner_sid"] == s]
            )
        )
        emit("clue_progress", {
            "players_done": players_fully_done,
            "total": len(all_players),
        }, room=room_id)

        if all_done:
            import time
            room["state"] = "guess_phase"
            room["guess_phase_start"] = time.time()

            # Build players_info for circle layout
            players_info = []
            for s in room["player_order"]:
                players_info.append({
                    "sid": s,
                    "name": room["players"].get(s, {}).get("name", "Unknown"),
                    "color": room["player_colors"].get(s, "#888"),
                })

            # Build canvas payload per player
            for player_sid in all_players:
                player_canvas = []
                for cc in room["canvas_cards"]:
                    entry = {
                        "card_id": cc["card_id"],
                        "owner_sid": cc["owner_sid"],
                        "owner_name": room["players"].get(cc["owner_sid"], {}).get("name", "Unknown"),
                        "clue": room["clues"].get(cc["owner_sid"], {}).get(cc["card_id"], ""),
                        "is_mine": cc["owner_sid"] == player_sid,
                    }
                    if cc["owner_sid"] == player_sid:
                        entry["word"] = cc["card"]["word"]
                    player_canvas.append(entry)

                socketio.emit("canvas_ready", {
                    "canvas": player_canvas,
                    "word_list": room["all_words"],
                    "players_info": players_info,
                    "player_colors": room["player_colors"],
                    "scores": room["correct_counts"],
                }, room=player_sid)

    @socketio.on("submit_canvas_guess")
    def on_submit_canvas_guess(data):
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()
        card_id = data.get("card_id")
        guess = data.get("guess", "").strip()[:100]

        room = rooms.get_room(room_id)
        if not room or room["state"] != "guess_phase":
            return
        if not guess:
            emit("error", {"message": "Guess cannot be empty."})
            return

        # Check if card is already claimed
        if card_id in room["card_claims"]:
            emit("error", {"message": "This card has already been claimed."})
            return

        is_correct, scores = rooms.check_canvas_guess(room_id, sid, card_id, guess)

        if is_correct:
            # Broadcast to entire room
            emit("card_claimed", {
                "card_id": card_id,
                "claimer_sid": sid,
                "claimer_name": room["players"].get(sid, {}).get("name", "Unknown"),
                "claimer_color": room["player_colors"].get(sid, "#888"),
                "scores": scores,
            }, room=room_id)

            # Check if all guessable cards are claimed
            # A card is guessable if at least one player exists who doesn't own it
            bot_sids = set(room.get("bots", []))
            real_sids = set(s for s in room["players"] if s not in bot_sids)
            guessable = []
            for cc in room["canvas_cards"]:
                owner = cc["owner_sid"]
                if DEBUG_MODE and len(real_sids) == 1 and owner in real_sids:
                    # Single real player can't guess their own cards — skip
                    continue
                guessable.append(cc)
            all_claimed = len(guessable) > 0 and all(
                cc["card_id"] in room["card_claims"] for cc in guessable)
            if all_claimed:
                room["state"] = "finished"
                final_scores = []
                for s in room["player_order"]:
                    final_scores.append({
                        "sid": s,
                        "name": room["players"].get(s, {}).get("name", "Unknown"),
                        "color": room["player_colors"].get(s, "#888"),
                        "score": room["correct_counts"].get(s, 0),
                    })
                final_scores.sort(key=lambda x: x["score"], reverse=True)
                emit("game_over", {"scores": final_scores}, room=room_id)
        else:
            # Only tell the guesser it was wrong
            emit("guess_wrong", {"card_id": card_id})

    @socketio.on("return_to_lobby")
    def on_return_to_lobby(data):
        sid = request.sid
        room_id = data.get("room_id", "").strip().upper()
        room = rooms.get_room(room_id)

        if not room:
            return

        # Reset game state
        room["state"] = "lobby"
        room["player_cards"] = {}
        room["canvas_cards"] = []
        room["player_colors"] = {}
        room["player_order"] = []
        room["all_words"] = []
        room["clues"] = {}
        room["card_claims"] = {}
        room["correct_counts"] = {}

        emit("returned_to_lobby", {
            "players": rooms.player_list(room_id),
        }, room=room_id)
