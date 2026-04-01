import csv
import os
from config import CSV_PATH, BOT_CLUES_PATH

FALLBACK_CARD = {
    "word": "Orange",
    "taboo_words": ["Color", "Fruit", "Juicy", "Citrus", "Red"],
}


def load_cards(path=CSV_PATH):
    """Load taboo cards from a CSV file.

    Expected CSV columns: word, taboo_words
    taboo_words are semicolon-separated.
    """
    cards = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["word"].strip()
                taboo_words = [
                    w.strip().strip('"') for w in row["taboo_words"].split(";")
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
