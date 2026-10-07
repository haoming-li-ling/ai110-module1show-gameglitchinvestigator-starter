from logic_utils import check_guess, get_range_for_difficulty, update_score

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
