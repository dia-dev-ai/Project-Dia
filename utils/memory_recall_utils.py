from utils.memory_utils import load_memories


FACTUAL_PREFIXES = (
    "who ",
    "what ",
    "when ",
    "where ",
    "why ",
    "how ",
    "is ",
    "are ",
    "do ",
    "does ",
    "did ",
)


def is_factual_query(text: str) -> bool:
    text = text.lower().strip()
    return text.startswith(FACTUAL_PREFIXES)


def select_relevant_memory(
    current_input: str,
    allow_recall: bool = True,
    max_lookback: int = 5
) -> str | None:
    """
    Select a single relevant memory conservatively.
    Only for personal / emotional conversation.
    """

    if not allow_recall:
        return None

    if is_factual_query(current_input):
        return None

    memories = load_memories()
    if not memories:
        return None

    recent = memories[-max_lookback:]

    # Prefer emotional memories only
    emotional = [m for m in reversed(recent) if m.get("emotional")]

    if emotional:
        return emotional[0]["content"]

    return None
