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

**What did you have to verify or fix manually?**

- **One fix caused a visible problem.** After the agent changed the attempt counter to start at 0, I ran the game and saw that "Attempts left" didn't go down after the first guess. The agent traced this to a Streamlit rerun issue that had been hidden by the old counter bug, and fixed it after I asked.
- **Design decisions were mine.** The agent asked before each fix, and I decided what counted as a bug. For example, I kept Hard at 5 attempts even though the agent pointed out that 1–200 can't always be solved in 5 guesses.
- **The agent's own check had a mistake.** In its first bug-reintroduction check, it copied pytest's cached files, so the app tests ran against the original code and wrongly passed. It noticed the suspicious result, found the cause and reran the check correctly.
- I made the commits myself, one per fix, and reviewed each change before committing.

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

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

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
