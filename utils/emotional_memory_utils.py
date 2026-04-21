import json
import os
from datetime import datetime

# =========================
# FILE PATHS & CONSTANTS
# =========================

EMOTIONAL_MEMORY_FILE = "memory/emotional_memory.json"
DEFAULT_DECAY_RATE = 0.02

# =========================
# INTERNAL LOAD / SAVE
# =========================

def _load_memory():
    if not os.path.exists(EMOTIONAL_MEMORY_FILE):
        return {
            "topic_sensitivity": {},
            "resolutions": {},
            "support_preferences": {}
        }

    with open(EMOTIONAL_MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_memory(data):
    os.makedirs(os.path.dirname(EMOTIONAL_MEMORY_FILE), exist_ok=True)
    with open(EMOTIONAL_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ======================================================
# A — TOPIC SENSITIVITY
# ======================================================

def register_topic_sensitivity(topic, note="", increment=0.1):
    """
    Creates or reinforces emotional sensitivity for a topic.
    Affects tone only.
    """

    data = _load_memory()
    topics = data["topic_sensitivity"]

    entry = topics.get(topic, {
        "sensitivity_score": 0.3,
        "last_triggered": None,
        "decay_rate": DEFAULT_DECAY_RATE,
        "notes": ""
    })

    entry["sensitivity_score"] = min(
        1.0, entry["sensitivity_score"] + increment
    )
    entry["last_triggered"] = datetime.utcnow().isoformat()

    if note:
        entry["notes"] = note

    topics[topic] = entry
    _save_memory(data)


def is_topic_sensitive(topic, threshold=0.4):
    """
    Returns True if topic is emotionally sensitive.
    """
    data = _load_memory()
    entry = data["topic_sensitivity"].get(topic)

    if not entry:
        return False

    return entry["sensitivity_score"] >= threshold


def decay_topic_sensitivity():
    """
    Gradually reduces sensitivity for all topics.
    Should be called periodically (session start or interval).
    """

    data = _load_memory()

    for entry in data["topic_sensitivity"].values():
        entry["sensitivity_score"] = max(
            0.0,
            entry["sensitivity_score"] - entry.get("decay_rate", DEFAULT_DECAY_RATE)
        )

    _save_memory(data)


# ======================================================
# B — EMOTIONAL RESOLUTION
# ======================================================

def mark_topic_resolved(topic, note="", confidence_increment=0.2):
    """
    Marks a topic as resolving over time.
    Prevents emotional hovering.
    """

    data = _load_memory()
    resolutions = data["resolutions"]

    entry = resolutions.get(topic, {
        "resolved": False,
        "resolution_confidence": 0.3,
        "last_confirmed": None,
        "notes": ""
    })

    entry["resolution_confidence"] = min(
        1.0, entry["resolution_confidence"] + confidence_increment
    )

    if entry["resolution_confidence"] >= 0.6:
        entry["resolved"] = True

    entry["last_confirmed"] = datetime.utcnow().isoformat()

    if note:
        entry["notes"] = note

    resolutions[topic] = entry
    _save_memory(data)


def is_topic_resolved(topic):
    """
    Returns True if topic is considered resolved.
    """
    data = _load_memory()
    entry = data["resolutions"].get(topic)
    return bool(entry and entry.get("resolved"))


# ======================================================
# C — SUPPORT PREFERENCE
# ======================================================

def update_support_preference(context, mode, note=""):
    """
    Learns how the user prefers to be supported in a context.
    mode: 'presence', 'advice', or 'mixed'
    """

    if mode not in ("presence", "advice", "mixed"):
        return

    data = _load_memory()
    prefs = data["support_preferences"]

    entry = prefs.get(context, {
        "preferred_mode": mode,
        "confidence": 0.3,
        "last_observed": None,
        "notes": ""
    })

    entry["preferred_mode"] = mode
    entry["confidence"] = min(1.0, entry["confidence"] + 0.1)
    entry["last_observed"] = datetime.utcnow().isoformat()

    if note:
        entry["notes"] = note

    prefs[context] = entry
    _save_memory(data)


def get_support_preference(context):
    """
    Returns preferred support mode for a context.
    Defaults to 'mixed'.
    """

    data = _load_memory()
    entry = data["support_preferences"].get(context)

    if not entry:
        return "mixed"

    return entry["preferred_mode"]
