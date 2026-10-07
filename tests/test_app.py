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
    assert "HIGHER" in at.warning[0].value


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
