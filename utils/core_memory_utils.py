import json
from pathlib import Path


CORE_IDENTITY_PATH = Path("data/core_identity.json")


def load_core_identity():
    """
    Load persistent user identity memory.
    Creates file if missing.
    """

    if not CORE_IDENTITY_PATH.exists():
        CORE_IDENTITY_PATH.parent.mkdir(parents=True, exist_ok=True)

        default_data = {
            "real_name": "P Jagdish Reddy",
            "nicknames": ["Pineapple", "Icey"]
        }

        with open(CORE_IDENTITY_PATH, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)

        return default_data

    with open(CORE_IDENTITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_core_identity(data: dict):
    with open(CORE_IDENTITY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def add_nickname(name: str):
    data = load_core_identity()

    if name not in data["nicknames"]:
        data["nicknames"].append(name)
        save_core_identity(data)


def remove_nickname(name: str):
    data = load_core_identity()

    if name in data["nicknames"]:
        data["nicknames"].remove(name)
        save_core_identity(data)


import random

def get_random_nickname(identity):
    """
    Return a nickname from the user's nickname pool.
    Returns None if no nicknames exist.
    """

    nicknames = identity.user_core.get("nicknames", [])

    if not nicknames:
        return None

    return random.choice(nicknames)