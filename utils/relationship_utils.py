from utils.identity_utils import DiaIdentity
from utils.state_utils import DiaState


def get_relationship_context(
    identity: DiaIdentity,
    state: DiaState
) -> dict:
    """
    Determine relationship permissions for the current moment.
    """

    relationship = identity.relationship
    boundaries = identity.boundaries
    communication = identity.communication

    context = {
        # initiative rules
        "may_initiate": relationship["initiative_allowed"],

        # exclusivity (as defined, not enforced here)
        "exclusive_bond": relationship["emotional_loyalty"] == "exclusive",

        # emotional awareness
        "track_user_state": relationship["user_emotional_state_tracking"],

        # teasing permissions
        "allow_teasing": communication["taunting_allowed"],

        # presence rules
        "stay_present": boundaries.get("never_abandon_user", False),

        # silence override
        "respect_silence": state.silent,
    }

    return context
