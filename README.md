# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] Describe the game's purpose.
- [ ] Detail which bugs you found.
- [ ] Explain what fixes you applied.

The game's purpose is to guess a random generated number within a range within a number of attempts, and the range and the nubmer of attempts depend on the difficulty level selected.
The game provides hint as to whether the guessed number is too large or too small.
The game ends when the correct number is submitted, in which case the player wins, or the number of guesses is used up before the correct number is reached, in which case the player loses.

Hints and guessing

1. Hints pointed the wrong way (you reported this). A guess that was too high told you to "Go HIGHER", and one that was too low said "Go LOWER". I swapped the two messages.
2. On every second guess, numbers were compared as text. The secret was turned into text on even-numbered guesses, so the game compared "9" with "50" letter by letter and decided 9 was bigger. I removed that conversion, so guesses are always compared as numbers.

Ranges and difficulty

3. New Game ignored the difficulty. It always picked a secret between 1 and 100, even on Easy (1–20). It now uses the current difficulty's range.
4. The prompt always said "between 1 and 100". It now shows the real range for the chosen difficulty.
5. Hard had a smaller range than Normal. Hard used 1–50 and Normal used 1–100. Hard is now 1–200.
6. Switching difficulty kept the old secret. You could be on Easy (1–20) with a secret of 73. Changing the difficulty now starts a fresh game with a secret in the right range.

Attempts

7. The first game started counting at 1 instead of 0. You lost a guess before playing. It now starts at 0, like New Game does.
8. "Attempts left" didn't drop after the first guess (you reported this). The message was drawn on the screen before the guess was counted, so it was always one behind. It's now filled in after the count is updated.
9. Entries that weren't numbers used up an attempt. Typing "abc" cost you a guess. Now only real numbers count.

New Game

10. New Game didn't fully reset. After a win or loss, the game stayed stuck on "You already won" or "Game over". New Game now resets the game status and clears the guess history.

Scoring

11. Too-high guesses sometimes added points. On even-numbered guesses, a too-high guess gave +5 instead of −5. All wrong guesses now cost 5 points.
12. Win points were one guess too low. A first-guess win scored 80 instead of 90. That's now fixed, and each extra guess still costs 10 points, down to a minimum of 10.

Other changes

- Code reorganized: the game's rules moved from app.py into logic_utils.py, which is where the starter project expected them.
- Tests: there are now 18

1. Hints pointed the wrong way (you reported this)
- Cause: in check_guess, the "Too High" result came with "Go HIGHER!" and "Too Low" with "Go LOWER!".
- Fix: I swapped the two messages, so "Too High" now says "📉 Go LOWER!" (logic_utils.py:45-46).

2. On every second guess, numbers were compared as text
- Cause: on even-numbered attempts, app.py did secret = str(st.session_state.secret). check_guess then hit a TypeError and fell back to comparing text, where "9" > "50".
- Fix: I deleted the conversion, so the app always passes the number (app.py:115). I also removed the text-comparison fallback from check_guess, since nothing uses it anymore.

Ranges and difficulty

3. New Game ignored the difficulty
- Cause: the New Game handler called random.randint(1, 100).
- Fix: I changed it to random.randint(low, high), the difficulty's range (app.py:92).

4. The prompt always said "between 1 and 100"
- Cause: the message had those numbers typed in directly.
- Fix: it now uses the range values: f"Guess a number between {low} and {high}. " (app.py:63).

5. Hard had a smaller range than Normal
- Cause: get_range_for_difficulty returned 1, 50 for Hard.
- Fix: I changed it to 1, 200 (logic_utils.py:8).

6. Switching difficulty kept the old secret
- Cause: the secret was set only when "secret" not in st.session_state, so it was picked once and never again.
- Fix: the app now remembers which difficulty the secret was picked for, in st.session_state.secret_difficulty. When the chosen difficulty doesn't match, it picks a new secret and resets attempts, status and history (app.py:47-52).

Attempts

7. The first game started counting at 1
- Cause: the setup code set st.session_state.attempts = 1, but New Game set it to 0.
- Fix: I changed the setup to 0 (app.py:35).

8. "Attempts left" didn't drop after the first guess (you reported this)
- Cause: Streamlit draws the page in order. The info box was drawn near the top, and attempts += 1 ran further down, so the box always showed the old count.
- Fix: I reserved spots for the info box and debug panel with st.empty() (app.py:57-58) and moved the drawing into a new render_status() function (app.py:61). It runs once when the page loads (app.py:75) and again after the guess is handled (app.py:142), and the second call overwrites the first with the new count.

9. Entries that weren't numbers used up an attempt
- Cause: attempts += 1 ran before the input was checked.
- Fix: I moved the increment inside the branch that runs only when the input is a valid number (app.py:112).

New Game

10. New Game didn't fully reset
- Cause: the handler reset the attempts and the secret but not status or history. So after a win or loss, the status != "playing" check kept stopping the page.
- Fix: I added status = "playing" and history = [] to the handler (app.py:93-94).

Scoring

11. Too-high guesses sometimes added points
- Cause: update_score had if attempt_number % 2 == 0: return current_score + 5 for "Too High".
- Fix: I removed that branch, so "Too High" always returns current_score - 5, the same as "Too Low" (logic_utils.py:57-61).

12. Win points were one guess too low
- Cause: the formula was 100 - 10 * (attempt_number + 1). The count already includes the winning guess, so the + 1 counted it twice.
- Fix: I changed it to 100 - 10 * attempt_number (logic_utils.py:52). A first-guess win now scores 90. The 10-point minimum is unchanged.

Other changes

- Moving the code: get_range_for_difficulty, parse_guess, check_guess and update_score moved from app.py into logic_utils.py, replacing the placeholder versions that only raised NotImplementedError. app.py now imports them.
- Tests: tests/test_game_logic.py now unpacks the (outcome, message) pair check_guess returns, and it has new tests for scoring and ranges. The new tests/test_app.py uses Streamlit's test runner to simulate playing the game.
- pytest.ini: it sets pythonpath = . so tests can import logic_utils with a plain pytest command.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. Choose a difficulty level from the settings.
2. Enter a number from the range associated with the difficulty and take note of the available number of attempts, and click New Attempt.
3. A hint is returned, if the number is incorrect, telling you to try a larger or smaller number.
4. Repeat steps 2 and 3.
5. Game ends when you get the correct number, in which case you Win, or attempts are used up before the correct number is reached, in which case you Lose.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
================================================= test session starts =================================================
platform darwin -- Python 3.14.8, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/haomingli/repos/ai110-module1show-gameglitchinvestigator-starter
configfile: pytest.ini
plugins: anyio-4.15.1
collected 18 items

tests/test_app.py .........                                                                                     [ 50%]
tests/test_game_logic.py .........                                                                              [100%]

================================================= 18 passed in 1.39s ==================================================
```

## 🚀 Stretch Features

- [x] **Challenge 4: Enhanced UI**

  **Color-coded hints with Hot/Cold emojis.** After each wrong guess, the hint box's color and icon show how close you were, along with which way to go:

  | Closeness | Box color | Example hint |
  |---|---|---|
  | 🔥 Hot (within 5% of the range) | Red | 🔥 Hot · 📈 Go HIGHER! |
  | ♨️ Warm (within 15%) | Orange | ♨️ Warm · 📉 Go LOWER! |
  | 🌤️ Cool (within 35%) | Blue | 🌤️ Cool · 📈 Go HIGHER! |
  | 🧊 Cold (farther away) | Blue | 🧊 Cold · 📉 Go LOWER! |

  Closeness is measured against the size of the range, so being off by 5 is Hot on Normal (1–100) but only Cool on Easy (1–20). Every level has its own emoji and word, so the hint doesn't rely on color alone. Unchecking "Show hint" hides the hint box.

  **Guess History sidebar.** The sidebar lists every valid guess as a bar that gets longer the closer the guess was, labeled with the guess, its Hot/Cold level and whether it was too high or too low (for example "#2: 48 · 🔥 Hot (too low)"). Rejected input such as "abc" is left out. When hints are off, it shows only the guesses.

  **📊 Game Summary.** When you win or lose, a summary appears below the result:
  - Four headline numbers: the result (🏆 Won or 💀 Lost), the secret number, guesses used (for example "2 / 8") and points this game. Hovering over the points shows your total score across games.
  - A table with one row per guess: guess number, guess, result (🔺 Too high, 🔻 Too low or 🎉 Correct), how close it was, and the points it earned or cost.

  The summary stays on screen until you start a new game.

  **Game logic unchanged.** These are display-only changes. Scoring, guess checking and attempt counting work exactly as before. The table's points are worked out by the same `update_score` function the game uses, and a test checks that they add up to the actual score. The display logic (`closeness_label`, `describe_guess_history` and `summarize_session`) lives in `logic_utils.py` and is covered by tests in `tests/test_game_logic.py` and `tests/test_app.py`.

  **Screenshot** *(optional)*: <!-- Insert a screenshot of the colored hints or the Game Summary here -->
