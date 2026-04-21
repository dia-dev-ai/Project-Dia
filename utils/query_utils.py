from enum import Enum, auto


class QueryType(Enum):
    SOCIAL = auto()
    EMOTIONAL = auto()
    FACTUAL = auto()
    MEMORY = auto()
    UNKNOWN = auto()


def classify_query(text: str) -> QueryType:
    text = text.lower().strip()

    if not text:
        return QueryType.UNKNOWN

    # 1️⃣ Presence / greetings FIRST (highest priority)
    presence_phrases = (
        "hello",
        "hi",
        "hey",
        "how are you",
        "are you there",
        "what's up",
        "whats up",
    )

    if any(text.startswith(p) for p in presence_phrases):
        return QueryType.SOCIAL

    # 2️⃣ Emotional statements
    emotional_markers = (
        "i am",
        "i'm",
        "i feel",
        "i’m",
        "feeling",
        "tired",
        "sad",
        "lonely",
        "stressed",
        "anxious",
    )

    if any(m in text for m in emotional_markers):
        return QueryType.EMOTIONAL

    # 3️⃣ Memory references
    memory_markers = (
        "remember",
        "last time",
        "before",
        "earlier",
        "again",
    )

    if any(m in text for m in memory_markers):
        return QueryType.MEMORY

    # 4️⃣ Factual (world knowledge only)
    if text.startswith(("who ", "what ", "when ", "where ", "why ", "how ")):
        return QueryType.FACTUAL

    return QueryType.SOCIAL
