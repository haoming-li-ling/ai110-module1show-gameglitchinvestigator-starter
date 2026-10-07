"""Game logic for the Glitchy Guesser number guessing game.

These functions hold the game's rules and contain no Streamlit code, so they
can be unit tested directly. ``app.py`` imports them and handles the UI.
"""

from __future__ import annotations

import re
from collections.abc import Sequence


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive range the secret number is drawn from.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"`` or ``"Hard"``.

    Returns:
        A ``(low, high)`` tuple of inclusive bounds: ``(1, 20)`` for Easy,
        ``(1, 100)`` for Normal and ``(1, 200)`` for Hard. Any other value
        falls back to the Normal range.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(
    raw: str | None,
    low: int | None = None,
    high: int | None = None,
) -> tuple[bool, int | None, str | None]:
    """Parse the player's raw input into a whole-number guess.

    Surrounding whitespace is ignored. Only plain whole numbers written with
    ASCII digits and an optional sign are accepted; decimals, exponents,
    underscores, hex and non-ASCII digits are rejected. When both ``low``
    and ``high`` are given, the guess must also fall within them.

    Args:
        raw: Text from the guess input box. ``None`` is treated as empty.
        low: Smallest allowed guess, inclusive. The range is only checked
            when ``high`` is also given.
        high: Largest allowed guess, inclusive.

    Returns:
        A ``(ok, guess, error)`` tuple. On success it is
        ``(True, guess, None)``; on failure it is ``(False, None, error)``,
        where ``error`` is a message suitable for showing to the player.

    Examples:
        >>> parse_guess(" 42 ")
        (True, 42, None)
        >>> parse_guess("50.9")
        (False, None, 'Enter a whole number.')
        >>> parse_guess("500", 1, 20)
        (False, None, 'Guess must be between 1 and 20.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    raw = raw.strip()
    if raw == "":
        return False, None, "Enter a guess."

    # Plain whole numbers only: no decimals, exponents, underscores or
    # non-ASCII digits, all of which int() or float() would otherwise accept
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


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a guess with the secret number.

    Args:
        guess: The player's guess.
        secret: The number the player is trying to find.

    Returns:
        An ``(outcome, message)`` tuple. ``outcome`` is ``"Win"``,
        ``"Too High"`` or ``"Too Low"``; ``message`` is the hint shown to the
        player, pointing toward the secret.

    Examples:
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def closeness_label(distance: int, low: int, high: int) -> str:
    """Label how far a guess is from the secret, relative to the range size.

    The distance is divided by the number of values in the range, so being
    off by 5 is "Hot" on a 1-100 range but only "Cool" on a 1-20 range.

    Args:
        distance: Absolute difference between the guess and the secret.
        low: Lower bound of the range, inclusive.
        high: Upper bound of the range, inclusive.

    Returns:
        ``"🎯 Correct"`` for a distance of 0. Otherwise, by the share of the
        range: ``"🔥 Hot"`` up to 5%, ``"♨️ Warm"`` up to 15%,
        ``"🌤️ Cool"`` up to 35% and ``"🧊 Cold"`` beyond that.

    Examples:
        >>> closeness_label(5, 1, 100)
        '🔥 Hot'
    """
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


def describe_guess_history(
    history: Sequence[int | str],
    secret: int,
    low: int,
    high: int,
) -> list[dict[str, int | float | str]]:
    """Describe how close each valid guess in the history was to the secret.

    The history also holds rejected input as raw text; those entries are
    skipped, so guesses are numbered consecutively from 1.

    Args:
        history: The player's past entries, oldest first. Ints are valid
            guesses; strings are rejected input.
        secret: The number the player is trying to find.
        low: Lower bound of the range, inclusive.
        high: Upper bound of the range, inclusive.

    Returns:
        One dict per valid guess, oldest first, with these keys:

        - ``"number"`` (int): position among valid guesses, starting at 1.
        - ``"guess"`` (int): the guessed value.
        - ``"outcome"`` (str): ``"Win"``, ``"Too High"`` or ``"Too Low"``.
        - ``"closeness"`` (float): 1.0 for the secret, falling linearly to
          0.0 at the full width of the range; clamped to ``[0.0, 1.0]``.
        - ``"label"`` (str): see :func:`closeness_label`.

    Examples:
        >>> rows = describe_guess_history([10, "abc", 50], 50, 1, 100)
        >>> [(r["number"], r["guess"], r["label"]) for r in rows]
        [(1, 10, '🧊 Cold'), (2, 50, '🎯 Correct')]
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


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Return the score after one guess.

    A win earns ``100 - 10 * attempt_number`` points, with a minimum of 10,
    so a first-guess win earns 90. A wrong guess costs 5 points.

    Args:
        current_score: Score before this guess.
        outcome: Result from :func:`check_guess`: ``"Win"``, ``"Too High"``
            or ``"Too Low"``. Any other value leaves the score unchanged.
        attempt_number: How many valid guesses have been made, including
            this one (1 for the first guess).

    Returns:
        The updated score. It can go below zero.

    Examples:
        >>> update_score(0, "Win", 1)
        90
        >>> update_score(100, "Too Low", 3)
        95
    """
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
