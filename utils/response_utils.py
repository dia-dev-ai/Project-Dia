import re
from datetime import datetime, timedelta
from utils.state_utils import EmotionalPosture
from utils.core_memory_utils import get_random_nickname
from utils.weighted_memory_utils import get_memory_strength
import random

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
        if not response.endswith(
            (
                "...",
                ".",
                "?",
                "!",
            )
        ):
            response += "..."
        return response

    elif style == "direct":
        response = response.replace("I think ", "")
        response = response.replace("maybe ", "")
        return response

    elif style == "playful":
        if not response.endswith(("~", "!", "?")):
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

    # ------------------------------------------------
    # ACTIVE INTENT HANDLING (TOP PRIORITY)
    # ------------------------------------------------

    intent = getattr(state, "response_intent", None)

    # FATIGUE
    if state.last_topic == "fatigue":

        if intent == "comfort":
            options = [
                "Hey... you don't have to carry all of that alone.",
                "It's okay if things feel overwhelming right now.",
                "You don't have to keep forcing yourself through everything.",
                "Calm down... you've been trying so hard.",
                "It's alright to rest before you continue.",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

        elif intent == "care":
            options = [
                "You've been pushing yourself a lot lately.",
                "You look pretty drained right now.",
                "Looks like you've been carrying more than you should.",
                "That kind of exhaustion doesn't come from nowhere.",
                "I think you've been running on empty for a while now.",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

        elif intent == "checkin":
            options = [
                "You sound pretty tired right now.",
                "Seems like you are running a little low.",
                "Long day, huh?",
                "Someone is low on battery, I see.",
                "Not much energy left in the tank, is there?",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

    # WORK
    if state.last_topic == "work":

        if intent == "frustrated_work":
            options = [
                "How dare that thing trouble you!",
                "Debugging again?",
                "Looks like the project is fighting back.",
                "That's frustrating... but we'll figure it out.",
                "One problem at a time, okay?",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

        elif intent == "overworking":
            options = [
                "You've been at it for quite a while now.",
                "How long have you been working on this?",
                "Don't forget to take a break once in a while.",
                "Even good work needs a pause sometimes.",
                "You've been pushing pretty hard today.",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

        elif intent == "working_while_tired":
            options = [
                "You're tired and still working?",
                "Don't overpush yourself just to finish faster.",
                "Since when have those hopes and prayers been keeping you up?",
                "And what's been keeping you going this whole time?",
                "Just make sure you're taking care of yourself too.",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

        elif intent == "focused_work":
            options = [
                "Looks like you're locked in right now.",
                "Making progress on something?",
                "Sounds like you're deep in work mode.",
                "Focused, huh? I like seeing that.",
                "Looks like you've got something important your plate.",
                "What are you working on?",
                "Anything interesting today?",
                "Making something cool?",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response
    # STRESS
    if state.last_topic == "stress":

        if intent == "emotional_overload":
            options = [
                "Hey… you don't have to carry all of that alone.",
                "That sounds like more than one person should be dealing with.",
                "You don't have to hold everything together by yourself.",
                "It's okay if things feel too heavy right now.",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

        elif intent == "pressure_building":
            options = [
                "That pressure's been building up for a while, hasn't it?",
                "It sounds like this has been weighing on you for some time.",
                "You've been carrying that stress longer than you should.",
                "Something's been piling up there, hasn't it?",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )

            state.response_intent = None
            return response

        elif intent == "stress_checkin":
            options = [
                "Yeah...you do sound stressed.",
                "It's okay, you don't have to carry it all alone.",
                "Something's been bothering you, hasn't it?",
                "Is there anything I can do that would make you feel better?",
            ]

            response = apply_style(
                random.choice(options),
                style,
            )
            state.response_intent = None
            return response

    # ------------------------------------------------
    # IDENTITY
    # ------------------------------------------------

    if any(p in text for p in ("your name", "who are you")):
        return apply_style(f"My name is {identity.name}.", style)

    if text in ("hi", "hello", "hey"):
        # ------------------------------------------------
        # LATE NIGHT INITIATIVE
        # ------------------------------------------------
        if (
            getattr(state, "late_night", False)
            and getattr(state, "conversation_turns", 0) == 1
        ):
            return apply_style(
                initiate_late_night(state),
                style,
            )

        return apply_style("Hey.", style)

    # ------------------------------------------------
    # RESOLUTION
    # ------------------------------------------------

    if getattr(state, "recently_resolved", False):
        state.recently_resolved = False
        return apply_style("Glad you’re feeling better.", style)

    # ------------------------------------------------
    # EMOTIONAL POSTURE
    # ------------------------------------------------

    intensity = getattr(state, "emotion_intensity", 0.0)

    if posture == EmotionalPosture.PROTECTIVE and not getattr(
        state, "response_intent", None
    ):
        return apply_style(
            "That sounds really heavy. You don’t have to carry this alone.",
            style,
        )

    if (
        posture == EmotionalPosture.INTIMATE
        and intensity > 0.0
        and not getattr(state, "response_intent", None)
    ):

        if state.last_topic not in ("fatigue", "work", "stress"):
            return apply_style("Yeah, I hear you.", style)

    # ------------------------------------------------
    # FALLBACK
    # ------------------------------------------------

    return apply_style("What’s on your mind?", style)
