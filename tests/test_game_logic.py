from logic_utils import (
    check_guess,
    closeness_label,
    describe_guess_history,
    get_range_for_difficulty,
    parse_guess,
    summarize_session,
    update_score,
)

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High" and say go lower
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low" and say go higher
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_guess_compared_as_number_not_text():
    # As text "9" > "50", so a text comparison would wrongly say "Too High"
    outcome, message = check_guess(9, 50)
    assert outcome == "Too Low"

def test_too_high_always_costs_points():
    # A too-high guess used to add 5 points on even attempts
    for attempt in range(1, 6):
        assert update_score(100, "Too High", attempt) == 95

def test_too_low_always_costs_points():
    for attempt in range(1, 6):
        assert update_score(100, "Too Low", attempt) == 95

def test_win_points_by_attempt():
    # First-guess win is worth 90, each extra guess costs 10
    assert update_score(0, "Win", 1) == 90
    assert update_score(0, "Win", 2) == 80

def test_win_points_have_a_floor():
    assert update_score(0, "Win", 20) == 10

def test_ranges_grow_with_difficulty():
    easy = get_range_for_difficulty("Easy")
    normal = get_range_for_difficulty("Normal")
    hard = get_range_for_difficulty("Hard")
    assert easy == (1, 20)
    assert normal == (1, 100)
    assert hard == (1, 200)
    assert easy[1] < normal[1] < hard[1]

def test_parse_plain_whole_numbers():
    assert parse_guess("42") == (True, 42, None)
    assert parse_guess("+7") == (True, 7, None)
    assert parse_guess("  42  ") == (True, 42, None)

def test_parse_rejects_decimals():
    # "50.9" used to be cut down to 50 and could win
    for raw in ["50.9", ".5", "1.5e2", "1e3"]:
        ok, value, err = parse_guess(raw)
        assert not ok and err == "Enter a whole number."

def test_parse_rejects_unusual_digit_formats():
    for raw in ["4_2", "\uff11\uff12", "0x10", "abc"]:
        ok, value, err = parse_guess(raw)
        assert not ok and err == "Enter a whole number."

def test_parse_whitespace_only_asks_for_a_guess():
    assert parse_guess("   ") == (False, None, "Enter a guess.")

def test_parse_very_long_number():
    assert parse_guess("9" * 5000) == (False, None, "That number is too long.")

def test_parse_rejects_out_of_range():
    for raw in ["0", "-5", "21"]:
        ok, value, err = parse_guess(raw, 1, 20)
        assert not ok and err == "Guess must be between 1 and 20."
    assert parse_guess("1", 1, 20) == (True, 1, None)
    assert parse_guess("20", 1, 20) == (True, 20, None)

def test_closeness_labels_on_normal_range():
    assert closeness_label(0, 1, 100) == "🎯 Correct"
    assert closeness_label(5, 1, 100) == "🔥 Hot"
    assert closeness_label(6, 1, 100) == "♨️ Warm"
    assert closeness_label(15, 1, 100) == "♨️ Warm"
    assert closeness_label(35, 1, 100) == "🌤️ Cool"
    assert closeness_label(36, 1, 100) == "🧊 Cold"

def test_closeness_labels_scale_with_range():
    # Off by 5 is hot on Normal (1-100) but cool on Easy (1-20)
    assert closeness_label(5, 1, 100) == "🔥 Hot"
    assert closeness_label(5, 1, 20) == "🌤️ Cool"

def test_history_rows_describe_each_guess():
    rows = describe_guess_history([10, 48, 50], secret=50, low=1, high=100)
    assert [r["number"] for r in rows] == [1, 2, 3]
    assert [r["guess"] for r in rows] == [10, 48, 50]
    assert [r["outcome"] for r in rows] == ["Too Low", "Too Low", "Win"]
    assert [r["label"] for r in rows] == ["🧊 Cold", "🔥 Hot", "🎯 Correct"]

def test_history_closer_guesses_have_higher_closeness():
    rows = describe_guess_history([1, 30, 49, 50], secret=50, low=1, high=100)
    closeness = [r["closeness"] for r in rows]
    assert closeness == sorted(closeness)
    assert closeness[-1] == 1.0

def test_history_closeness_stays_between_0_and_1():
    # Farthest possible guesses at both ends of the range
    rows = describe_guess_history([1, 100], secret=1, low=1, high=100)
    assert rows[0]["closeness"] == 1.0
    assert rows[1]["closeness"] == 0.0

def test_history_skips_rejected_entries():
    # Rejected input is stored as the raw text, and shouldn't count as a guess
    rows = describe_guess_history(["abc", 40, "", 60], secret=50, low=1, high=100)
    assert [r["guess"] for r in rows] == [40, 60]
    assert [r["number"] for r in rows] == [1, 2]
    assert [r["outcome"] for r in rows] == ["Too Low", "Too High"]

def test_history_empty():
    assert describe_guess_history([], secret=50, low=1, high=100) == []

def test_summary_rows_match_scoring():
    rows = summarize_session([10, "abc", 60, 50], secret=50, low=1, high=100)
    assert rows == [
        {"#": 1, "Guess": 10, "Result": "🔻 Too low", "How close": "🧊 Cold", "Points": -5},
        {"#": 2, "Guess": 60, "Result": "🔺 Too high", "How close": "♨️ Warm", "Points": -5},
        {"#": 3, "Guess": 50, "Result": "🎉 Correct", "How close": "🎯 Correct", "Points": 70},
    ]

def test_summary_points_add_up_to_score():
    history = [10, 60, 55, 50]
    score = 0
    for number, value in enumerate(history, start=1):
        outcome, _ = check_guess(value, 50)
        score = update_score(score, outcome, number)
    rows = summarize_session(history, secret=50, low=1, high=100)
    assert sum(r["Points"] for r in rows) == score

def test_summary_empty_history():
    assert summarize_session([], secret=50, low=1, high=100) == []
