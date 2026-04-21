import json
from utils.core_memory_utils import load_core_identity
from pathlib import Path
from types import MappingProxyType


class DiaIdentity:
    """
    Immutable wrapper around dia_core.json.
    Identity is read-only at runtime.
    """

    def __init__(self, raw_data: dict):
        # freeze top-level sections
        self._identity = MappingProxyType(raw_data["identity"])
        self._personality = MappingProxyType(raw_data["personality"])
        self._relationship = MappingProxyType(raw_data["relationship_model"])
        self._communication = MappingProxyType(raw_data["communication"])
        self._emotional_engine = MappingProxyType(raw_data["emotional_engine"])
        self._boundaries = MappingProxyType(raw_data["boundaries"])
        self._truth_policy = MappingProxyType(raw_data["truth_policy"])
        self._execution_flags = MappingProxyType(raw_data["execution_flags"])

    # ---- exposed read-only properties ----

    @property
    def identity(self):
        return self._identity

    @property
    def personality(self):
        return self._personality

    @property
    def relationship(self):
        return self._relationship

    @property
    def communication(self):
        return self._communication

    @property
    def emotional_engine(self):
        return self._emotional_engine

    @property
    def boundaries(self):
        return self._boundaries

    @property
    def truth_policy(self):
        return self._truth_policy

    @property
    def execution_flags(self):
        return self._execution_flags

    # ---- convenience accessors ----

    @property
    def name(self):
        return self._identity["name"]

    @property
    def bond_priority(self):
        return self._identity["bond_priority"]

    @property
    def emotional_loyalty(self):
        return self._relationship["emotional_loyalty"]


def load_identity(
    path: str = "identity/dia_core.json"
) -> DiaIdentity:
    """
    Load and freeze Dia's identity.
    Fails loudly if identity is missing or malformed.
    """

    identity_path = Path(path)

    if not identity_path.exists():
        raise FileNotFoundError(f"Identity file not found: {identity_path}")

    with open(identity_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # required top-level sections (strict)
    required_sections = [
        "identity",
        "personality",
        "relationship_model",
        "communication",
        "emotional_engine",
        "boundaries",
        "truth_policy",
        "execution_flags",
    ]

    for section in required_sections:
        if section not in raw:
            raise ValueError(f"Missing required identity section: {section}")

    identity = DiaIdentity(raw)

    # Attach persistent user identity memory
    identity.user_core = load_core_identity()

    return identity