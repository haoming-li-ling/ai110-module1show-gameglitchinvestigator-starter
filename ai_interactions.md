# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (Claude Opus 5.5) in the terminal. I started with one bug, "The hint given after each guess is the wrong direction. fix it", and then had it work through the rest of the game's bugs. I asked it to "fix one by one; ask for directions before moving to next bug", so I approved each fix before it moved on. Later I asked it to move the game logic into `logic_utils.py`, add tests for every fix, and handle edge-case inputs.

**What did the agent do?**

- Read `app.py` and found the hint messages swapped in `check_guess`. While there, it found that the secret was turned into a string on even attempts, which flipped hints a different way.
- Fixed 12 bugs, one per step, each in `app.py` or `logic_utils.py`: hint direction, text comparison of the secret, New Game range, prompt range, New Game not resetting, the attempt counter starting at 1, "Attempts left" lagging one guess, invalid input using an attempt, too-high guesses adding points, win points off by one, the Hard range, and difficulty switches keeping the old secret.
- Moved `get_range_for_difficulty`, `parse_guess`, `check_guess` and `update_score` into `logic_utils.py`, and changed `app.py` to import them.
- Wrote unit tests (`tests/test_game_logic.py`) and Streamlit `AppTest` tests (`tests/test_app.py`) that simulate playing the game. It added `pytest.ini` so a plain `pytest` command works.
- Tested the input parser with unusual inputs and tightened it: only whole numbers, inside the difficulty's range, with spaces trimmed.
- Ran `pytest` and simulated games after each change. To show the tests catch real bugs, it put each old bug back in a scratch copy of the repo and confirmed a test failed.
- Wrote a summary commit message that lists all the fixes.
- Built a **Guess History** sidebar from the prompt "Implement a 'Guess History' sidebar that visualizes how close your previous guesses were. Add tests for it." It added `closeness_label` and `describe_guess_history` to `logic_utils.py`. They turn each valid guess into a 0–1 "closeness" score and a label: 🎯 Correct, 🔥 Hot, ♨️ Warm, 🌤️ Cool or 🧊 Cold. The labels scale with the difficulty's range, so off by 5 is "Hot" on Normal but "Cool" on Easy. In `app.py`, each guess shows as a progress bar, longer when closer, captioned with the guess, its label and too high/too low. The sidebar respects the "Show hint" checkbox and hides closeness when hints are off. It's redrawn after every guess, using the same reserved-spot trick as "Attempts left", so it never lags behind.
- Added **structured, user-friendly output** from the prompt "Add structured and user-friendly output to the game such as color-coded hints, emojis for 'Hot/Cold' states, or a summary table of the game session (without breaking core game logic)."
  - **Color-coded hints:** the hint box now follows the Hot/Cold level from the Guess History sidebar. 🔥 Hot is red, ♨️ Warm is orange, and 🌤️ Cool and 🧊 Cold are blue, with the emoji as the box's icon (for example "🔥 Hot · 📈 Go HIGHER!"). The emoji and word mean color is never the only signal.
  - **Game Summary:** when a game is won or lost, the game shows four headline numbers (result, secret, guesses used and points this game) and a table with each guess's result, closeness and points. The new `summarize_session` function in `logic_utils.py` builds the table and works out the points with the existing `update_score`, so it always matches the real score.
  - **Game logic untouched:** the only lines removed from `app.py` were the two that showed the old yellow hint. Scoring, guess checking and attempt counting didn't change.

**What did you have to verify or fix manually?**

- **One fix caused a visible problem.** After the agent changed the attempt counter to start at 0, I ran the game and saw that "Attempts left" didn't go down after the first guess. The agent traced this to a Streamlit rerun issue that had been hidden by the old counter bug, and fixed it after I asked.
- **Design decisions were mine.** The agent asked before each fix, and I decided what counted as a bug. For example, I kept Hard at 5 attempts even though the agent pointed out that 1–200 can't always be solved in 5 guesses.
- **The agent's own check had a mistake.** In its first bug-reintroduction check, it copied pytest's cached files, so the app tests ran against the original code and wrongly passed. It noticed the suspicious result, found the cause and reran the check correctly.
- I made the commits myself, one per fix, and reviewed each change before committing.
- **Guess History design choices to review:** the agent chose to show closeness as labels plus bars rather than exact distances, since exact distances would make the game trivial. It also chose to hide closeness when hints are off. I should confirm both match what I want, and check how the sidebar looks in the browser, since the agent only checked it through Streamlit's test runner.
- **Output feature review:** one existing test broke because it looked for the hint in the yellow box only, and a "Cold" hint is now blue. The agent changed the test to find the hint in any box rather than changing the game. It also found that Streamlit quietly moves an emoji at the start of an alert into the box's icon, so it set the icon explicitly. I should check the hint colors and the summary layout in the browser, and confirm that hiding the hint on a winning guess is what I want.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Guess compared as text on even attempts ("9" vs secret 50) | "add tests for all of them" | `test_hint_correct_on_even_attempts`: guess 9 twice and check that the second hint says HIGHER | Yes; it fails if the bug is put back | Checks hints at the app level, where the bug was |
| "Attempts left" lagging one guess behind | "add tests for all of them" | `test_attempts_left_drops_on_first_guess`: after one guess, the info box shows "Attempts left: 7" | Yes; it fails if the bug is put back | Checks what's on screen, since that's where the bug showed |
| Decimal input "50.9" cut down to 50 and able to win | "Fix all and fill in ai_interactions.md" | `test_parse_rejects_decimals`: "50.9", ".5", "1.5e2" and "1e3" are all rejected with "Enter a whole number." | Yes | A guess should be a whole number, not rounded |
| Out-of-range guess (500 on Easy) using an attempt | "Fix all and fill in ai_interactions.md" | `test_parse_rejects_out_of_range` and `test_out_of_range_guess_does_not_use_an_attempt` | Yes | Typos shouldn't cost a guess; the edges (1 and 20) are still accepted |
| Spaces-only input | "Fix all and fill in ai_interactions.md" | `test_parse_whitespace_only_asks_for_a_guess`: "   " gives "Enter a guess." | Yes | Blank input should get the same message as an empty box |
| Very long number (5,000 digits) | "Fix all and fill in ai_interactions.md" | `test_parse_very_long_number`: it's rejected with "That number is too long." | Yes | Python refuses to convert integers this long, so it needs its own message |
| Rejected input mixed into Guess History | "Implement a 'Guess History' sidebar … Add tests for it." | `test_history_skips_rejected_entries` and `test_history_sidebar_shows_each_guess`: "abc" is left out, and the guesses are numbered 1, 2 without gaps | Yes; it fails if rejected input is counted | History keeps rejected text for debugging, but it isn't a guess |
| Closeness at the extremes of the range | Same as above | `test_history_closeness_stays_between_0_and_1`: the farthest guess gives 0.0 and the exact one 1.0 | Yes | The progress bar needs a value between 0 and 1 |
| Same distance on different difficulties | Same as above | `test_closeness_labels_scale_with_range`: off by 5 is "Hot" on 1–100 but "Cool" on 1–20 | Yes; it fails if labels ignore the range | "Close" should depend on how big the range is |
| Guess History after the game ends | Same as above | `test_history_sidebar_shows_winning_guess_after_game_ends` | Yes; it fails if the sidebar isn't drawn before the game-over stop | Players should still see their history after winning or losing |
| Hints turned off | Same as above | `test_history_hides_closeness_when_hints_off`: only guess numbers and values are shown | Yes | Closeness is a hint, so it follows the "Show hint" setting |
| Hint color at each closeness level | "Add structured and user-friendly output … (without breaking core game logic)." | `test_hint_color_matches_closeness`: guesses that are Hot, Warm, Cool and Cold give a red, orange, blue and blue box with the right icon and text | Yes, after the agent set the icon explicitly | Each level should look different, and the direction must still be correct |
| Summary points vs. the real score | Same as above | `test_summary_points_add_up_to_score` and `test_summary_after_win`: the table's points add up to the score the game awarded (−5 + 80 = 75) | Yes | The table must never disagree with the actual scoring |
| Summary after a loss | Same as above | `test_summary_after_loss`: six misses on Easy show "💀 Lost", "6 / 6" and −30 points | Yes | The summary should cover losses as well as wins |
| Summary timing | Same as above | `test_no_summary_while_playing` and `test_summary_stays_after_game_ends`: no table mid-game; it stays after the game ends and clears on New Game | Yes | A summary mid-game would clutter the screen; it belongs at the end |
| Existing hint test after the color change | Same as above | The agent changed `test_hint_correct_on_even_attempts` to find the hint in any box, not just the yellow one | Failed at first, then passed after the test was updated | The game was correct; the test was tied to the old box color |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
add professional-grade docstrings to every function in logic_utils.py; review against PEP8 style
```

**Linting output before:**

The agent ran `ruff` (0.16.10) on `logic_utils.py` with the PEP 8 (`E`, `W`), naming (`N`), docstring (`D`) and type-annotation (`ANN`, `RUF013`) rules, at PEP 8's 79-character line limit:

```
$ ruff check --isolated --select E,W,N,D,ANN,RUF013 --line-length 79 logic_utils.py
logic_utils.py:1:1: D100 Missing docstring in public module
logic_utils.py:4:5: ANN201 Missing return type annotation for public function `get_range_for_difficulty`
logic_utils.py:15:5: ANN201 Missing return type annotation for public function `parse_guess`
logic_utils.py:15:32: RUF013 PEP 484 prohibits implicit `Optional`
logic_utils.py:15:50: RUF013 PEP 484 prohibits implicit `Optional`
logic_utils.py:16:5: D212 [*] Multi-line docstring summary should start at the first line
logic_utils.py:17:80: E501 Line too long (85 > 79)
logic_utils.py:28:80: E501 Line too long (87 > 79)
logic_utils.py:44:5: ANN201 Missing return type annotation for public function `check_guess`
logic_utils.py:44:17: ANN001 Missing type annotation for function argument `guess`
logic_utils.py:44:24: ANN001 Missing type annotation for function argument `secret`
logic_utils.py:45:5: D212 [*] Multi-line docstring summary should start at the first line
logic_utils.py:58:5: ANN201 Missing return type annotation for public function `closeness_label`
logic_utils.py:59:80: E501 Line too long (82 > 79)
logic_utils.py:72:5: ANN201 Missing return type annotation for public function `describe_guess_history`
logic_utils.py:72:28: ANN001 Missing type annotation for function argument `history`
logic_utils.py:73:5: D212 [*] Multi-line docstring summary should start at the first line
logic_utils.py:77:80: E501 Line too long (87 > 79)
logic_utils.py:97:5: ANN201 Missing return type annotation for public function `update_score`
Found 19 errors.
```

**Changes applied:**

- **Docstrings:** I added a module docstring and rewrote every function's docstring in the Google style: a one-line summary, then `Args`, `Returns` and `Examples` sections. They now document behavior that wasn't written down before. For example, unknown difficulties fall back to Normal, the range check needs both `low` and `high`, the closeness bands are 5%, 15% and 35%, and the score can go below zero.
- **Executable examples:** every `Examples` section is a doctest. `python -m doctest logic_utils.py` passes, so the examples can't silently go out of date.
- **Implicit `Optional` (RUF013):** `low: int = None` became `low: int | None = None`, since the old hint claimed `int` while allowing `None`.
- **Type hints (ANN):** I added argument and return types to every function, for example `parse_guess(...) -> tuple[bool, int | None, str | None]`. I added `from __future__ import annotations` so the `X | None` syntax also works on Python versions before 3.10.
- **Line length (E501):** I wrapped the long docstrings and the regex comment to fit in 79 characters. Long signatures now put one argument per line.
- **Result:** with the Google docstring convention, `ruff check ... --config "lint.pydocstyle.convention='google'"` reports "All checks passed!", and all 38 tests still pass. The code's behavior is unchanged.
- **Not applied:** `ruff format` would reflow the dict literal in `describe_guess_history`. That's a formatter preference rather than a PEP 8 rule, so I kept the existing style. `app.py` and the tests still have 6 lines over 79 characters; they were outside the scope of this prompt.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
