import os

# Toggle to "true" in .env to simulate the email provider failing,
# to prove the submission still succeeds even when this breaks.
EMAIL_FORCE_FAIL = os.getenv("EMAIL_FORCE_FAIL", "false").lower() == "true"


def send_confirmation(submission: dict):
    """Fake email side effect. Failure here must never break the caller."""
    if EMAIL_FORCE_FAIL:
        raise RuntimeError("Simulated email provider outage")
    print(f"[email] Confirmation sent for submission {submission.get('id')}")