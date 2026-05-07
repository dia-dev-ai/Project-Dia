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

    def shift_emotion(self, emotion, intensity):
        self.dia_emotion = emotion
        self.dia_emotion_intensity = intensity

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
