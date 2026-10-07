# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

    Attempts feel weird, some not registering. The hints are unhelpful. Cannot restart game after losing.
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| 30 (secret: 38)| higher | lower | NA |
| any number after New Game | a hint | no hint, Game over message stays | NA |
| select easy/hard | prompt updates to 20 and 50 | prompt stays 100 | NA |
| Submit Guess beyond allowed | Attempts left stow at 0 | prompt goes to negative numbers | NA |
|  Guess beyond allowed | Attempts left stops at 0 | prompt goes to negative numbers | NA |


---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

    Claude Code CLI
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

    Fixing the New Game logic. The off-by-one error in attempts left is indeed gone after the fix.
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

    Unfortunately, this code base is a piece of cake for Claude Code and all of what it did seems reasonable to me.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

    If repeated testing no longer reproduces the wrong behavior.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.

    Entering a number and clicking new attempt repeatedly until the number of attempts is used up. The counter kept decreasing. This means that there is a bug with the game termination logic.
- Did AI help you design or understand any tests? How?

    AI added a test for each bug fixed. It confirmed that each fix when removed would cause the codebase to fail at least one of the tests.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
    Think of a Streamlit app as a script that gets re-read from the beginning every time you touch the page.

    Most apps sit and wait for a click, then run only the code for that click. Streamlit is simpler. Whenever you click a button, type something or change a setting, it throws away the page and runs your whole program again from the first line to the last, redrawing everything along the way. Each of those full passes is a "rerun."

    This makes the app forgetful. Since the program starts over every time, anything it worked out on the last pass is gone. If the game picked its secret number the ordinary way, it would pick a new one every time you clicked. To get around this, Streamlit gives you a "memory box" called session_state that survives between reruns. The game keeps the things it must remember there: the secret, how many guesses you've made, your score and your guess history.

    Order matters, because the page is drawn as the program runs. Our "Attempts left" bug came from exactly this. The program drew the "Attempts left" message near the top, and only further down did it notice your guess and add one to the count. By then the message was already on the screen with the old number. You only saw the right number on the next pass, which is why it seemed stuck on your first guess. The fix was to save a spot for that message and fill it in at the end, after the count had changed.

    There are two ways to cut a pass short. One says "stop here and start over right away," which New Game uses so the page instantly redraws as a fresh game. The other says "stop here and don't draw anything else," which the game uses once you've won or lost, so the guess area doesn't show up.

    In short, Streamlit redraws the whole page from scratch on every interaction, and it remembers only what you put in its memory box.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

  Claude is eager to discover bugs on its own, often several at a time. I ask it to fix them one by one, asking for direction before moving to the next one, so I can have a clean commit history.
- What is one thing you would do differently next time you work with AI on a coding task?
    Let it examine the code base first.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
    AI generated code can contain extraenous logic that is completely non-obvious from the functionality, like the various tests for even vs odd attempts.
