import random

ADJECTIVES = [
    "Swift", "Bold", "Calm", "Dizzy", "Eager", "Fancy", "Gentle", "Happy",
    "Icy", "Jolly", "Keen", "Lively", "Mellow", "Noble", "Odd", "Plucky",
    "Quick", "Rusty", "Sly", "Tough", "Upbeat", "Vivid", "Witty", "Zany",
    "Bright", "Clever", "Daring", "Frosty", "Grand", "Hasty", "Lucky",
    "Mighty", "Nimble", "Proud", "Quiet", "Sunny", "Tiny", "Warm", "Wild",
    "Cosmic", "Crispy", "Fuzzy", "Golden", "Humble", "Peppy", "Sneaky",
]

NOUNS = [
    "Fox", "Owl", "Bear", "Wolf", "Hawk", "Lynx", "Crow", "Deer",
    "Frog", "Hare", "Newt", "Seal", "Wren", "Dove", "Moth", "Crab",
    "Otter", "Finch", "Robin", "Raven", "Moose", "Crane", "Panda",
    "Koala", "Gecko", "Lemur", "Bison", "Viper", "Squid", "Macaw",
    "Llama", "Ibis", "Lark", "Mole", "Pike", "Swan", "Toad", "Wasp",
    "Beetle", "Falcon", "Walrus", "Badger", "Parrot", "Salmon", "Donkey",
]


def generate_name():
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
