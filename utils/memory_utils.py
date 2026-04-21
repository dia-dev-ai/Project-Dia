import json
from pathlib import Path
from datetime import datetime
from utils.identity_utils import DiaIdentity

MEMORY_PATH = Path("state/longterm_memory.json")


def _load_raw_memory() -> list:
    if not MEMORY_PATH.exists():
        return []
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw_memory(memory: list):
    MEMORY_PATH.parent.mkdir(exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def store_memory(
    content: str,
    emotional: bool,
    identity: DiaIdentity
):
    """
    Store a memory entry respecting Dia's emotional_engine rules.
    """

    memory = _load_raw_memory()

    weight = (
        identity.emotional_engine["memory_weighting"]["emotional_events"]
        if emotional
        else identity.emotional_engine["memory_weighting"]["casual_talk"]
    )

    entry = {
        "content": content,
        "emotional": emotional,
        "weight": weight,
        "timestamp": datetime.utcnow().isoformat()
    }

    memory.append(entry)
    _save_raw_memory(memory)


def load_memories() -> list:
    """
    Load all stored memories.
    """
    return _load_raw_memory()
