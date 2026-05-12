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

    if state.late_night_stage == 3:
        return "Long night."

    return None


def apply_style(response, style):

    if style == "soft":
        response = response.replace("?", "...")

    elif style == "direct":
        response = response.replace("maybe ", "")

    elif style == "playful":
        if not response.endswith("~"):
            response += " ~"

    return response


def generate_response(
    user_input,
    posture,
    state,
    relationship,
    identity,
    style,
):
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
        return apply_style(initiative, style)

    # ----------------------------
    # IDENTITY
    # ----------------------------
    if any(p in text for p in ("your name", "who are you")):
        return apply_style(f"My name is {identity.name}.", style)

    if text in ("hi", "hello", "hey"):
        return apply_style("Hey.", style)

    # ----------------------------
    # RESOLUTION
    # ----------------------------
    if getattr(state, "recently_resolved", False):
        state.recently_resolved = False
        return apply_style("Glad you’re feeling better.", style)

    # ----------------------------
    # EMOTIONAL RESPONSES
    # ----------------------------
    intensity = getattr(state, "emotion_intensity", 0.0)
    intent = getattr(state, "response_intent", None)

    if state.last_topic == "fatigue":
        return apply_style(
            "hey... you don't have to carry everything alone right now.",
            style,
        )
    elif intent == "care":
        return apply_style(
            "You’ve been pushing yourself a lot… maybe slow down a bit.",
            style,
        )

    elif intent == "checkin":
        return apply_style(
            "You sound a little tired… did you get enough rest?",
            style,
        )

    if posture == EmotionalPosture.PROTECTIVE:
        return apply_style(
            "That sounds really heavy. You don’t have to carry this alone.",
            style,
        )

    if posture == EmotionalPosture.INTIMATE and intensity > 0.0:

        if state.last_topic not in ("fatigue", "work", "stress"):
            return apply_style("Yeah, I hear you.", style)

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
            return apply_style(
                "You’ve been at this for a while… how’s it going?",
                style,
            )

        elif strength > 0.4:
            return apply_style("Still working on that?", style)

        else:
            return apply_style("How’s that going?", style)

    # Fatigue
    if state.last_topic == "fatigue":
        strength = get_memory_strength("fatigue")

        if strength > 0.7:
            return apply_style(
                "You’ve been pushing yourself a lot… you should get some rest.",
                style,
            )

        elif strength > 0.4:
            return apply_style("Still feeling that way?", style)

        else:
            return "Yeah, I hear you."
    # Stress
    if state.last_topic == "stress":
        strength = get_memory_strength("stress")

        if strength > 0.7:
            return apply_style(
                "That’s been weighing on you for a while… you don’t have to handle it alone.",
                style,
            )

        elif strength > 0.4:
            return apply_style("Still feeling overwhelmed?", style)

        else:
            return apply_style("That sounds stressful.", style)

    return apply_style("What’s on your mind?", style)
