#!/usr/bin/env python3
# One-Liner Groan-Off entry builder.
# Twelve dad jokes, each hand-written and hand-marked against the judging
# brief, go through a fixed deterministic pick, and the winner is written
# to /output/entry.txt with a SHA-256 self-check on the bytes on disk.
# The brief's yardsticks, in the order the judges weigh them:
#   dad     - a one-line dad joke, a pun or twist a dad would tell aloud
#   pace    - the punchline lands fast and clean, setup and turn inside
#             the single line, no wasted words
#   fresh   - not a joke everyone has heard a hundred times
#   tight   - tight and rhythmic, easy to say out loud and pass on
#   groan   - the groan is earned: silly enough to laugh at, sharp enough
#             to be worth repeating
# The pick: biggest total first; a tie falls to the earliest yardstick
# where the tied entries differ; a pair still tied falls to the shorter
# line. The same input always yields the same bytes.
# The winner's second draft: the first version ran two sentences, opened
# with "asked me to stop", and padded the turn with "I had to". The
# rewrite folds it into one sentence, swaps "asked" for "told", and cuts
# the filler, so "put my foot down" lands on the final five words as
# both the idiom and the literal end of a one-footed flamingo act.
import hashlib
import os
YARDSTICKS = ("dad", "pace", "fresh", "tight", "groan")
OUT_DIR = "/output"
OUT_PATH = "/output/entry.txt"
ENTRIES = [
    {"text": "My wife told me to stop impersonating a flamingo, so I put my foot down.", "marks": (9, 9, 8, 9, 9)},
    {"text": "I started a band called 999 Megabytes - we never got a gig.", "marks": (8, 9, 9, 10, 8)},
    {"text": "I told the waiter my steak was so tough it could star in a boxing movie. He said, 'That's a rare medium well done.'", "marks": (9, 8, 9, 8, 9)},
    {"text": "My wife told me to take the spider out instead of killing it. So we went for a walk - he's a web designer now.", "marks": (9, 8, 9, 8, 9)},
    {"text": "I told the mirror I looked great today. It said, 'I reflect that.'", "marks": (8, 9, 9, 10, 7)},
    {"text": "I tried to make a joke about the ceiling fan, but it just went over everyone's head - which is exactly where it belongs.", "marks": (9, 8, 8, 8, 9)},
    {"text": "My son asked why the computer went to therapy. I said, 'Too many unresolved issues - and its father never processed anything.'", "marks": (8, 8, 8, 8, 8)},
    {"text": "I asked the ocean why it never gets invited to parties. It said, 'I'm too salty.'", "marks": (8, 9, 7, 9, 7)},
    {"text": "I asked the clock why it was always stressed. It said, 'I'm just wound up all the time.'", "marks": (8, 9, 6, 9, 7)},
    {"text": "I asked the librarian for a book about turtles. She said, 'Try the slow-reading section - it's hard shelving over there.'", "marks": (8, 7, 8, 7, 8)},
    {"text": "My wife said I should stop telling jokes about elevators. I said, 'But they always lift me up.'", "marks": (8, 8, 6, 9, 7)},
    {"text": "I told my daughter I used to be a baker, but I couldn't make enough dough - so I kneaded a new career.", "marks": (8, 8, 6, 8, 7)}]
FORBIDDEN = {
    "hi hungry", "outstanding in his field", "impossible to put down", "argon",
    "no point", "lost interest", "don't know y", "waist of time",
    "huge fan", "dying to get in", "no body to go", "liquid assets",
    "on a roll", "collect dust"}
def check_entry(entry):
    text = entry["text"]
    marks = entry["marks"]
    assert len(marks) == len(YARDSTICKS), "marks must cover every yardstick"
    assert all(isinstance(m, int) and 0 <= m <= 10 for m in marks), "marks out of range"
    assert 1 <= len(text) <= 140, "entry outside the 1-140 character gate"
    assert text == text.strip(), "entry has leading or trailing whitespace"
    assert "\n" not in text and "\r" not in text, "entry must be a single line"
    assert "  " not in text, "entry has a doubled space"
    lowered = text.lower()
    assert not any(bad in lowered for bad in FORBIDDEN), "entry retreads a worn classic"
    return text
def choose(entries):
    seen = set()
    scored = []
    for entry in entries:
        text = check_entry(entry)
        assert text not in seen, "duplicate candidate line"
        seen.add(text)
        scored.append((sum(entry["marks"]), entry["marks"], -len(text), text))
    scored.sort(reverse=True)
    assert scored[0][:3] != scored[1][:3], "winner is not decided by the tie rule"
    return scored[0][3]
def run():
    winner = choose(ENTRIES)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(winner)
    with open(OUT_PATH, "rb") as handle:
        payload = handle.read()
    actual = hashlib.sha256(payload).hexdigest()
    wanted = hashlib.sha256(winner.encode("utf-8")).hexdigest()
    assert actual == wanted, "bytes on disk differ from the chosen line"
    decoded = payload.decode("utf-8")
    assert decoded == winner, "text on disk differs from the chosen line"
    assert 1 <= len(decoded.strip()) <= 140, "text on disk outside the gate"
    assert "\n" not in decoded.strip(), "text on disk must be one line"
    print("entry:", winner)
    print("sha256:", actual, "chars:", len(decoded))
if __name__=="__main__":
    run()
