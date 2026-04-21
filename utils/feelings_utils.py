from utils.state_utils import EmotionalPosture, DiaState
from utils.identity_utils import DiaIdentity


DISTRESS_MARKERS = [
    "i'm not okay",
    "im not okay",
    "i feel lost",
    "i'm tired",
    "im tired",
    "i feel empty",
    "i don't know",
    "idk",
    "help",
]


PLAYFUL_MARKERS = [
    "haha",
    "lol",
    "jk",
    "tease",
    "joking",
]


def infer_distress(user_input: str) -> bool:
    text = user_input.lower().strip()
    return any(marker in text for marker in DISTRESS_MARKERS)


def infer_playfulness(user_input: str) -> bool:
    text = user_input.lower().strip()
    return any(marker in text for marker in PLAYFUL_MARKERS)


def determine_emotional_posture(
    user_input: str,
    state: DiaState,
    identity: DiaIdentity
) -> EmotionalPosture:
    """
    Decide Dia's emotional posture for this turn.
    Identity is immutable. State is mutable.
    """

    # 1. Distress → protective (highest priority)
    if infer_distress(user_input):
        return EmotionalPosture.PROTECTIVE

    # 2. Late night → intimate if allowed
    if state.late_night:
        return EmotionalPosture.INTIMATE

    # 3. Playfulness (only if allowed by identity)
    if identity.communication["taunting_allowed"]:
        if infer_playfulness(user_input):
            return EmotionalPosture.PLAYFUL

    # 4. Default → caring
    return EmotionalPosture.CARING
