import random
import streamlit as st

from logic_utils import (
    check_guess,
    closeness_label,
    describe_guess_history,
    get_range_for_difficulty,
    parse_guess,
    summarize_session,
    update_score,
)

# Hint box color by closeness: red when hot, orange when warm, blue when cool
HINT_BOXES = {
    "🔥 Hot": st.error,
    "♨️ Warm": st.warning,
    "🌤️ Cool": st.info,
    "🧊 Cold": st.info,
}

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Start a fresh game when the difficulty changes so the secret fits the new range
if st.session_state.get("secret_difficulty") != difficulty:
    st.session_state.secret_difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.status = "playing"
    st.session_state.history = []

st.subheader("Make a guess")

# Placeholders so the status can be redrawn after a guess updates session state
info_box = st.empty()
debug_box = st.empty()
history_box = st.sidebar.empty()


def render_history():
    with history_box.container():
        st.subheader("Guess History")
        rows = describe_guess_history(
            st.session_state.history, st.session_state.secret, low, high
        )
        if not rows:
            st.caption("No guesses yet.")
            return
        for row in rows:
            if show_hint:
                direction = "" if row["outcome"] == "Win" else f" ({row['outcome'].lower()})"
                st.progress(
                    row["closeness"],
                    text=f"#{row['number']}: {row['guess']} · {row['label']}{direction}",
                )
            else:
                st.caption(f"#{row['number']}: {row['guess']}")
        if not show_hint:
            st.caption("Turn on hints to see how close each guess was.")


def render_status():
    render_history()
    info_box.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )
    with debug_box.container():
        with st.expander("Developer Debug Info"):
            st.write("Secret:", st.session_state.secret)
            st.write("Attempts:", st.session_state.attempts)
            st.write("Score:", st.session_state.score)
            st.write("Difficulty:", difficulty)
            st.write("History:", st.session_state.history)


def render_summary():
    rows = summarize_session(
        st.session_state.history, st.session_state.secret, low, high
    )
    st.subheader("📊 Game Summary")
    col_result, col_secret, col_guesses, col_points = st.columns(4)
    col_result.metric(
        "Result", "🏆 Won" if st.session_state.status == "won" else "💀 Lost"
    )
    col_secret.metric("Secret", st.session_state.secret)
    col_guesses.metric("Guesses", f"{len(rows)} / {attempt_limit}")
    col_points.metric(
        "Points this game",
        sum(row["Points"] for row in rows),
        help=f"Total score across games: {st.session_state.score}",
    )
    st.table(rows)


raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# Draw after the widgets so render_history can read show_hint
render_status()

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    render_summary()
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint and outcome != "Win":
            label = closeness_label(
                abs(guess_int - st.session_state.secret), low, high
            )
            emoji, word = label.split(" ", 1)
            HINT_BOXES[label](f"{word} · {message}", icon=emoji)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

        if st.session_state.status != "playing":
            render_summary()

    render_status()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
