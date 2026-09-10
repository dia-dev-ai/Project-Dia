from datetime import datetime

memory_store = {}


def register_memory(topic: str, intensity: float):
    """
    Adds or strengthens a memory.
    """

    now = datetime.now()

    if topic not in memory_store:
        memory_store[topic] = {
            "strength": 0.3,
            "emotion_weight": intensity,
            "last_updated": now,
        }
    else:
        memory_store[topic]["strength"] += 0.2
        memory_store[topic]["emotion_weight"] = max(
            memory_store[topic]["emotion_weight"], intensity
        )
        memory_store[topic]["last_updated"] = now


def get_memory_strength(topic: str):
    if topic not in memory_store:
        return 0.0
    return memory_store[topic]["strength"]


def decay_memory():
    """
    Gradually weakens memories over time.
    """
    for topic in list(memory_store.keys()):
        memory_store[topic]["strength"] *= 0.95

        if memory_store[topic]["strength"] < 0.1:
            del memory_store[topic]


def get_strongest_memory():
    if not memory_store:
        return None
    return max(memory_store.items(), key=lambda x: x[1]["strength"])[0]
