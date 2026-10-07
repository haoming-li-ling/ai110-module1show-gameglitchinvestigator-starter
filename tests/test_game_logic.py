from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

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
