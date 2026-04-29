'''
Functions to load taboo cards and bot clues from CSV files.
'''

import csv
import os
from config import CSV_PATH, BOT_CLUES_PATH

FALLBACK_CARD = {
    "word": "Orange",
    "taboo_words": ["Color", "Fruit", "Juicy", "Citrus", "Red"],
}


def load_cards(path=CSV_PATH):
    """Load taboo cards from blather_round_taboo.csv.

    Expected CSV columns: name, category, difficulty, taboo_1..taboo_5
    """
    cards = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                difficulty = row.get("difficulty", "").strip().lower()
                if difficulty != "easy":
                    continue
                word = row["name"].strip()
                taboo_words = [
                    row[col].strip()
                    for col in ("taboo_1", "taboo_2", "taboo_3", "taboo_4", "taboo_5")
                    if row.get(col, "").strip()
                ]
                cards.append({"word": word, "taboo_words": taboo_words})

    if not cards:
        cards.append(FALLBACK_CARD)

    return cards


def load_bot_clues(path=BOT_CLUES_PATH):
    """Load bot clues from CSV. Returns dict mapping word -> clue."""
    clues = {}
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                clues[row["word"].strip()] = row["clue"].strip()
    return clues
