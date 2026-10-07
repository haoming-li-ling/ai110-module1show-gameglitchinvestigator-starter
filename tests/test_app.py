from streamlit.testing.v1 import AppTest

# Path is relative to this test file
APP_PATH = "../app.py"


def start_game(secret=50, difficulty="Normal"):
    """Load the app with a known secret for the given difficulty."""
    at = AppTest.from_file(APP_PATH)
    at.session_state["secret_difficulty"] = difficulty
    at.session_state["secret"] = secret
    at.run()
    if difficulty != "Normal":
        # Switching resets the secret, so set it again afterwards
        at.sidebar.selectbox[0].select(difficulty).run()
        at.session_state["secret"] = secret
    return at


def guess(at, value):
    at.text_input[0].input(str(value))
    at.button[0].click().run()


def click_new_game(at):
    at.button[1].click().run()


def hint_boxes(at):
    """(box type, icon, text) for each hint box: the ones with "Go ..."."""
    boxes = []
    for kind in ("error", "warning", "info", "success"):
        for box in getattr(at, kind):
            if "Go " in box.value:
                boxes.append((kind, box.icon, box.value))
    return boxes


def hint_text(at):
    [(kind, icon, text)] = hint_boxes(at)
    return text


def attempts_left_text(at):
    return at.info[0].value


def test_attempts_start_at_zero():
    at = start_game()
    assert at.session_state.attempts == 0
    assert "Attempts left: 8" in attempts_left_text(at)


def test_attempts_left_drops_on_first_guess():
    at = start_game(secret=50)
    guess(at, 10)
    assert "Attempts left: 7" in attempts_left_text(at)


def test_invalid_guess_does_not_use_an_attempt():
    at = start_game()
    guess(at, "abc")
    assert at.session_state.attempts == 0
    assert "Attempts left: 8" in attempts_left_text(at)
    assert at.error[0].value == "Enter a whole number."


def test_out_of_range_guess_does_not_use_an_attempt():
    at = start_game(difficulty="Easy")
    guess(at, 500)
    assert at.session_state.attempts == 0
    assert at.error[0].value == "Guess must be between 1 and 20."


def test_hint_correct_on_even_attempts():
    # The secret used to become text on even attempts, flipping some hints
    at = start_game(secret=50)
    guess(at, 9)
    guess(at, 9)
    assert at.session_state.attempts == 2
    assert "HIGHER" in hint_text(at)


def test_prompt_shows_difficulty_range():
    at = start_game(difficulty="Easy")
    assert "between 1 and 20" in attempts_left_text(at)


def test_new_game_secret_uses_difficulty_range():
    at = start_game(difficulty="Easy")
    for _ in range(20):
        click_new_game(at)
        assert 1 <= at.session_state.secret <= 20


def test_new_game_resets_after_win():
    at = start_game(secret=50)
    guess(at, 50)
    assert at.session_state.status == "won"

    click_new_game(at)
    assert at.session_state.status == "playing"
    assert at.session_state.history == []
    assert at.session_state.attempts == 0

    # A new guess is accepted instead of showing "You already won"
    at.session_state["secret"] = 50
    guess(at, 10)
    assert at.session_state.attempts == 1


def test_switching_difficulty_starts_new_game():
    at = start_game(secret=73)
    guess(at, 10)
    at.sidebar.selectbox[0].select("Easy").run()
    assert 1 <= at.session_state.secret <= 20
    assert at.session_state.attempts == 0
    assert at.session_state.history == []
    assert "between 1 and 20" in attempts_left_text(at)


def test_rerun_keeps_secret_on_same_difficulty():
    at = start_game(secret=50)
    at.run()
    assert at.session_state.secret == 50


def history_bars(at):
    """Text of each Guess History bar in the sidebar."""
    return [bar.proto.text for bar in at.sidebar.get("progress")]


def test_history_sidebar_starts_empty():
    at = start_game()
    assert at.sidebar.subheader[0].value == "Guess History"
    assert any(c.value == "No guesses yet." for c in at.sidebar.caption)
    assert history_bars(at) == []


def test_history_sidebar_shows_each_guess():
    at = start_game(secret=50)
    guess(at, 10)
    guess(at, "abc")
    guess(at, 48)
    assert history_bars(at) == [
        "#1: 10 · 🧊 Cold (too low)",
        "#2: 48 · 🔥 Hot (too low)",
    ]


def test_history_bars_grow_as_guesses_get_closer():
    at = start_game(secret=50)
    guess(at, 10)
    guess(at, 48)
    values = [bar.proto.value for bar in at.sidebar.get("progress")]
    assert values[0] < values[1]


def test_history_sidebar_shows_winning_guess_after_game_ends():
    at = start_game(secret=50)
    guess(at, 50)
    at.run()
    assert history_bars(at) == ["#1: 50 · 🎯 Correct"]


def test_history_hides_closeness_when_hints_off():
    at = start_game(secret=50)
    guess(at, 48)
    at.checkbox[0].uncheck().run()
    assert history_bars(at) == []
    captions = [c.value for c in at.sidebar.caption]
    assert "#1: 48" in captions
    assert "Turn on hints to see how close each guess was." in captions


def test_history_clears_on_new_game():
    at = start_game(secret=50)
    guess(at, 10)
    click_new_game(at)
    assert history_bars(at) == []


def test_hint_color_matches_closeness():
    # Normal range 1-100: off by 2 is hot, 10 warm, 30 cool, 45 cold
    cases = [
        (48, "error", "🔥", "Hot · 📈 Go HIGHER!"),
        (60, "warning", "♨️", "Warm · 📉 Go LOWER!"),
        (20, "info", "🌤️", "Cool · 📈 Go HIGHER!"),
        (95, "info", "🧊", "Cold · 📉 Go LOWER!"),
    ]
    for value, kind, icon, text in cases:
        at = start_game(secret=50)
        guess(at, value)
        assert hint_boxes(at) == [(kind, icon, text)]


def test_hint_hidden_when_hints_off():
    at = start_game(secret=50)
    at.checkbox[0].uncheck().run()
    guess(at, 48)
    assert hint_boxes(at) == []


def test_no_summary_while_playing():
    at = start_game(secret=50)
    guess(at, 10)
    assert at.table == []
    assert "📊 Game Summary" not in [s.value for s in at.subheader]


def test_summary_after_win():
    at = start_game(secret=50)
    guess(at, 40)
    guess(at, 50)
    assert "📊 Game Summary" in [s.value for s in at.subheader]
    metrics = {m.label: m.value for m in at.metric}
    assert metrics == {
        "Result": "🏆 Won",
        "Secret": "50",
        "Guesses": "2 / 8",
        "Points this game": "75",
    }
    table = at.table[0].value
    assert list(table["Guess"]) == [40, 50]
    assert list(table["Result"]) == ["🔻 Too low", "🎉 Correct"]
    assert list(table["Points"]) == [-5, 80]
    # Points in the table add up to the score the game awarded
    assert at.session_state.score == 75


def test_summary_after_loss():
    at = start_game(secret=50, difficulty="Easy")
    at.session_state["secret"] = 15
    for value in [1, 2, 3, 4, 5, 6]:
        guess(at, value)
    assert at.session_state.status == "lost"
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Result"] == "💀 Lost"
    assert metrics["Guesses"] == "6 / 6"
    assert metrics["Points this game"] == "-30"
    assert len(at.table[0].value) == 6


def test_summary_stays_after_game_ends():
    at = start_game(secret=50)
    guess(at, 50)
    at.run()
    assert len(at.table) == 1
    click_new_game(at)
    assert at.table == []
