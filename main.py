from datetime import datetime
import random

from utils.identity_utils import load_identity
from utils.state_utils import DiaState, EmotionalPosture
from utils.query_utils import classify_query, QueryType
from utils.response_utils import generate_response
from utils.relationship_utils import get_relationship_context
from utils.weighted_memory_utils import register_memory, decay_memory
from utils.emotional_memory_utils import (
    register_topic_sensitivity,
    mark_topic_resolved,
    is_topic_sensitive,
    decay_topic_sensitivity,
)

# ----------------------------
# EXIT PHRASES
# ----------------------------
EXIT_PHRASES = [
    "bye",
    "goodbye",
    "good night",
    "goodnight",
    "see you",
    "talk later",
    "i'll go",
    "i am going",
    "that's all",
    "exit",
]


# ----------------------------
# TIME CHECK
# ----------------------------
def is_late_night_now():
    hour = datetime.now().hour
    return hour >= 23 or hour < 5


def main():
    identity = load_identity()
    state = DiaState()
    relationship = get_relationship_context(identity, state)

    decay_topic_sensitivity()

    state.late_night_stage = 0
    state.last_initiative_time = None

    print(f"{identity.name} is online.")

    try:
        while True:
            # ----------------------------
            # INPUT
            # ----------------------------
            user_input = input("> ").strip()

            if not user_input:
                continue

            t = user_input.lower().replace("'", "")

            state.decay_emotions()

            # ----------------------------
            # EXIT
            # ----------------------------
            if any(phrase in t for phrase in EXIT_PHRASES):
                msg = (
                    "Get some rest… you have already done enough."
                    if is_late_night_now()
                    else "Take care… I’ll be here waiting for you."
                )

                print(f"{identity.name}: {msg}")
                break

            # ----------------------------
            # STATE UPDATE
            # ----------------------------
            state.previous_user_input = state.last_user_input
            state.last_user_input = user_input
            state.late_night = is_late_night_now()

            query_type = classify_query(user_input)

            topic = "general"
            intensity = 0.0
            resolved_signal = False
            prev = state.last_topic
            response = None

            # ----------------------------
            # STRESS
            # ----------------------------
            if any(
                word in t
                for word in ["stressed", "pressure", "overwhelmed", "too much"]
            ):
                state.shift_emotion("concerned", 0.9, "user sounded stressed")

                topic = "stress"
                intensity = 0.7

                if any(
                    x in t for x in ["breaking down", "cant handle", "cant take it"]
                ):
                    responses = [
                        "Hey… you don’t have to carry all of that at once.",
                        "That sounds like it’s getting too heavy… take a second.",
                    ]

                elif any(x in t for x in ["overwhelmed", "too much"]):
                    responses = [
                        "That sounds like a lot to deal with at once.",
                        "Seems like things are stacking up more than usual.",
                    ]

                else:
                    responses = [
                        "Feels like there’s a bit of pressure on you.",
                        "Something’s weighing on you a little, isn’t it.",
                    ]

                response = random.choice(responses)

            # ----------------------------
            # WORK
            # ----------------------------
            if any(word in t for word in ["coding", "working", "project"]):
                state.shift_emotion("focused", 0.5, "user is working on projects")

                topic = "work"
                intensity = 0.3

                if any(x in t for x in ["stuck", "not working"]):
                    responses = [
                        "Hmm… something’s not clicking i guess?",
                        "You’ve been at it for a while… hit a wall?",
                    ]

                elif any(x in t for x in ["hours", "long"]):
                    responses = [
                        "You’ve been on this for quite some time.",
                        "That’s a long stretch of focus…",
                    ]

                else:
                    responses = (
                        [
                            "You were tired… and you're still working?",
                            "Didn’t even rest after saying you were tired, huh.",
                        ]
                        if prev == "fatigue"
                        else [
                            "You’re deep into it right now.",
                            "Seems like you’re really focused on that.",
                        ]
                    )

                response = random.choice(responses)

            # ----------------------------
            # FATIGUE
            # ----------------------------
            if "cant" in t and "anymore" in t:
                state.shift_emotion("concerned", 0.9, "user sounded exhausted")

                topic = "fatigue"
                intensity = 0.9

                responses = [
                    "Hey… it’s okay. You don’t have to carry everything right now.",
                    "Take a moment… breathe. You don’t have to keep going like this.",
                ]

                response = random.choice(responses)

            elif any(x in t for x in ["exhausted", "burnt out"]):
                state.shift_emotion("concerned", 0.7, "user sounded exhausted")

                topic = "fatigue"
                intensity = 0.7

                responses = [
                    "You’ve been pushing yourself a lot… maybe slow down a bit.",
                    "That sounds like more than just being tired… you should take a break.",
                ]

                response = random.choice(responses)

            elif any(x in t for x in ["tired", "sleepy", "low energy"]):
                state.shift_emotion("concerned", 0.5, "user sounded tired")

                topic = "fatigue"
                intensity = 0.4

                responses = [
                    "You sound a bit tired… did you get enough rest?",
                    "Hmm… seems like you're running low on energy.",
                ]

                response = random.choice(responses)

            # ----------------------------
            # APPLY STATE + MEMORY
            # ----------------------------
            state.last_topic = topic
            state.emotion_intensity = intensity
            state.recently_resolved = resolved_signal

            register_memory(topic, intensity)
            decay_memory()

            if query_type == QueryType.EMOTIONAL and intensity >= 0.5:
                register_topic_sensitivity(topic)

            if resolved_signal:
                mark_topic_resolved(topic)

            sensitive = is_topic_sensitive(topic)

            posture = (
                EmotionalPosture.PROTECTIVE
                if sensitive and not resolved_signal and intensity >= 0.7
                else EmotionalPosture.INTIMATE
            )

            # ----------------------------
            # DEFAULT RESPONSE
            # ----------------------------
            if topic == "general":
                state.shift_emotion("playful", 0.3, "normal conversation")
                # --- STYLE DETECTION  ---

            style = "normal"

            concern = state.get_emotion_level("concerned")
            playful = state.get_emotion_level("playful")
            focus = state.get_emotion_level("focused")

            if concern > 0.2:
                style = "soft"

            elif playful > 0.6:
                style = "playful"

            elif focus > 0.6:
                style = "direct"

            print(f"[STYLE MODE]: {style}")

            if response is None:
                response = generate_response(
                    user_input,
                    posture,
                    state,
                    relationship,
                    identity,
                )

            dominant = state.get_dominant_emotions()

            if dominant == "concerned":
                response = response.replace(".", "...")

            elif dominant == "focused":
                response = response.replace("?", ".")

            elif dominant == "playful":
                pass
            # --- EMOTION BLENDING ---
            concern = state.get_emotion_level("concerned")
            focus = state.get_emotion_level("focused")

            if concern > 0.5 and focus > 0.3:
                response += " Just don't overpush yourself while working..."

            # --- CONTEXTUAL CALLBACK ---
            if dominant == "concerned" and "exhausted" in state.emotion_reason:
                if random.random() < 0.35:
                    response += " You've been pushing yourself pretty hard lately..."

            print(f"{identity.name}: {response}")

    except KeyboardInterrupt:
        print(f"\n{identity.name}: I’ll be right here when you come back.")


if __name__ == "__main__":
    main()
