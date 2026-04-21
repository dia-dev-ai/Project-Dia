import re
from datetime import datetime, timedelta
from utils.state_utils import EmotionalPosture
from utils.core_memory_utils import get_random_nickname
from utils.weighted_memory_utils import get_memory_strength


LATE_NIGHT_PHRASES = (
    "it's late",
    "its late",
    "late night",
    "midnight",
    "still awake",
    "can't sleep",
    "cant sleep",
)


def can_initiate(state):
    if not getattr(state, "late_night", False):
        return False

    if getattr(state, "emotion_intensity", 0.0) >= 0.7:
        return False

    now = datetime.now()
    last = getattr(state, "last_initiative_time", None)

    if last and now - last < timedelta(minutes=15):
        return False

    return True


def initiate_late_night(state):
    state.late_night_stage += 1
    state.last_initiative_time = datetime.now()

    # Stage 1
    if state.late_night_stage == 1:
        return "You’re still up… what’s keeping you awake, mister?"

    # Stage 2
    if state.late_night_stage == 2:
        return "Still here."

    # Stage 3
    if state.late_night_stage == 3:
        return "Long night."

    return None


def generate_response(user_input, posture, state, relationship, identity):
    text = re.sub(r"[^\w\s]", "", user_input.lower()).strip()

    # phrase-based awareness
    if any(p in text for p in LATE_NIGHT_PHRASES):
        state.late_night = True

    # ----------------------------
    # LATE-NIGHT INITIATIVE
    # ----------------------------
    initiative = None
    if can_initiate(state):
        initiative = initiate_late_night(state)

    if initiative:
        return initiative

    # ----------------------------
    # IDENTITY
    # ----------------------------
    if any(p in text for p in ("your name", "who are you")):
        return f"My name is {identity.name}."

    if text in ("hi", "hello", "hey"):
        return "Hey."

    # ----------------------------
    # RESOLUTION
    # ----------------------------
    if getattr(state, "recently_resolved", False):
        state.recently_resolved = False
        return "Glad you’re feeling better."

    # ----------------------------
    # EMOTIONAL RESPONSES
    # ----------------------------
    intensity = getattr(state, "emotion_intensity", 0.0)

    if posture == EmotionalPosture.PROTECTIVE:
        return "That sounds really heavy. You don’t have to carry this alone."

    if posture == EmotionalPosture.INTIMATE and intensity > 0.0:
        # Allow memory system to take over for known topics
        if state.last_topic not in ("fatigue", "work", "stress"):
            return "Yeah, I hear you."

       # ----------------------------
    # NEUTRAL
    # ----------------------------
    nickname = get_random_nickname(identity)

    # ----------------------------
    # TOPIC-BASED MEMORY RESPONSE
    # ----------------------------

    # Work
    if state.last_topic == "work":
        strength = get_memory_strength("work")

        if strength > 0.7:
            return "You’ve been at this for a while… how’s it going?"

        elif strength > 0.4:
            return "Still working on that?"

        else:
            return "How’s that going?"

    # Fatigue
    if state.last_topic == "fatigue":
        strength = get_memory_strength("fatigue")

        if strength > 0.7:
            return "You’ve been pushing yourself a lot… you should get some rest."

        elif strength > 0.4:
            return "Still feeling that way?"

        else:
            return "Yeah, I hear you."
    # Stress
    if state.last_topic == "stress":
        strength = get_memory_strength("stress")

        if strength > 0.7:
            return "That’s been weighing on you for a while… you don’t have to handle it alone."

        elif strength > 0.4:
            return "Still feeling overwhelmed?"

        else:
            return "That sounds stressful."

    # FINAL fallback
    return "What’s on your mind?"