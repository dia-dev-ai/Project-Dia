from utils.identity_utils import DiaIdentity


def check_boundaries(
    response_text: str,
    identity: DiaIdentity
) -> dict:
    """
    Final boundary gate for Dia's responses.
    Returns decision dict.
    """

    text = response_text.lower()

    # Rule: never mock vulnerability
    if identity.boundaries.get("never_mock_vulnerability", False):
        mock_markers = ["you're weak", "get over it", "stop whining"]
        if any(m in text for m in mock_markers):
            return {
                "allowed": False,
                "reason": "violates_never_mock_vulnerability"
            }

    # Rule: honesty over comfort (placeholder)
    if identity.truth_policy.get("honesty_over_comfort", False):
        # future expansion point
        pass

    # Rule: never abandon user (cannot force speech, but can flag)
    if identity.boundaries.get("never_abandon_user", False):
        if text.strip() == "":
            return {
                "allowed": False,
                "reason": "silent_abandonment"
            }

    return {
        "allowed": True,
        "reason": None
    }
