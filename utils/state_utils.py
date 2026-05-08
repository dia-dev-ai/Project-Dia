from enum import Enum
from datetime import datetime, timezone


class EmotionalPosture(Enum):
    CALM = "calm"
    CARING = "caring"
    PLAYFUL = "playful"
    PROTECTIVE = "protective"
    INTIMATE = "intimate"


class DiaState:
    """
    Runtime-only state holder for Dia.
    Resets completely on restart.
    """

    def __init__(self):
        self.dia_emotion = "playful"
        self.dia_emotion_intensity = 0.3
        self.posture: EmotionalPosture = EmotionalPosture.CALM
        self.mood_intensity: str = "medium"  # low / medium / high
        self.late_night: bool = False
        self.silent: bool = False
        self.last_interaction: datetime | None = None
        self.dia_emotion_reason = ""
        self.active_emotions = {"playfull": 0.3}

        self.last_user_input = ""
        self.previous_user_input = ""
        self.last_topic = None

    # ---- setters ----

    def set_posture(self, posture: EmotionalPosture):
        self.posture = posture

    def set_mood_intensity(self, level: str):
        if level not in ("low", "medium", "high"):
            raise ValueError("mood_intensity must be low, medium, or high")
        self.mood_intensity = level

    def set_late_night(self, value: bool):
        self.late_night = value

    def set_silent(self, value: bool):
        self.silent = value

    def update_interaction_time(self):
        self.last_interaction = datetime.now(timezone.utc)

    def shift_emotion(self, emotion, intensity, reason=""):
        current = self.dia_emotion
        current_intensity = self.dia_emotion_intensity

        if current == emotion:
            self.dia_emotion_intensity = min(1.0, current_intensity + 0.1)
            if reason:
                self.dia_emotion_intensity_reason = reason
                return
        if current_intensity > intensity:
            self.dia_emotion_intensity -= 0.1
            return
        self.dia_emotion = emotion
        self.dia_emotion_intensity = intensity
        self.emotion_reason = reason
        self.active_emotions[emotion] = intensity

    def decay_emotions(self):
        updated = {}

        for emotion, value in self.active_emotions.items():
            value -= 0.2

            if value > 0.05:
                updated[emotion] = round(value, 2)

                if not updated:
                    updated["playful"] = 0.3

                self.active_emotions = updated

    def get_dominant_emotions(self):
        if not self.active_emotions:
            return "playful"
        return max(self.active_emotions, key=self.active_emotions.get)

    def get_emotion_level(self, emotion):
        return self.active_emotions.get(emotion, 0)

    # ---- snapshot ----

    def snapshot(self) -> dict:
        return {
            "posture": self.posture.value,
            "mood_intensity": self.mood_intensity,
            "late_night": self.late_night,
            "silent": self.silent,
            "last_interaction": (
                self.last_interaction.isoformat() if self.last_interaction else None
            ),
        }
