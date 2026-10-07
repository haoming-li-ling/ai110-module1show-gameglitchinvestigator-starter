import re


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess, optionally checking it is within [low, high].

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    raw = raw.strip()
    if raw == "":
        return False, None, "Enter a guess."

    # Only plain whole numbers: no decimals, exponents, underscores or non-ASCII digits
    if not re.fullmatch(r"[+-]?[0-9]+", raw):
        return False, None, "Enter a whole number."

    try:
        value = int(raw)
    except ValueError:
        # Python refuses to convert integers with thousands of digits
        return False, None, "That number is too long."

    if low is not None and high is not None and not low <= value <= high:
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def closeness_label(distance: int, low: int, high: int):
    """Describe how far a guess is from the secret, relative to the range size."""
    if distance == 0:
        return "🎯 Correct"
    ratio = distance / (high - low + 1)
    if ratio <= 0.05:
        return "🔥 Hot"
    if ratio <= 0.15:
        return "♨️ Warm"
    if ratio <= 0.35:
        return "🌤️ Cool"
    return "🧊 Cold"


def describe_guess_history(history, secret: int, low: int, high: int):
    """
    Build one row per valid guess describing how close it was to the secret.

    Entries that aren't ints (rejected input kept in history) are skipped.
    Returns: list of dicts with keys number, guess, outcome, closeness (0.0-1.0), label
    """
    rows = []
    span = high - low
    for value in history:
        if not isinstance(value, int):
            continue
        distance = abs(value - secret)
        closeness = 1.0 - distance / span if span else 1.0
        outcome, _ = check_guess(value, secret)
        rows.append({
            "number": len(rows) + 1,
            "guess": value,
            "outcome": outcome,
            "closeness": min(max(closeness, 0.0), 1.0),
            "label": closeness_label(distance, low, high),
        })
    return rows


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
