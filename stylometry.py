"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures capture sentence length spread, vocabulary repetition, and
non-terminal punctuation density. Their combination is a heuristic, not proof
of authorship.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how often selected non-terminal marks occur?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    Coefficient of variation of sentence word counts.

    Returns:
        A non-negative value; zero means no measured spread. A single sentence
        also returns zero because its spread cannot be estimated.
    """
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    if len(lengths) < 2:
        return 0.0

    mean_length = statistics.mean(lengths)
    if mean_length == 0:
        return 0.0
    return statistics.stdev(lengths) / mean_length


def type_token_ratio(text: str) -> float:
    """
    Unique lowercase word tokens over all lowercase word tokens.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    Count commas, semicolons, colons, dashes, and brackets per word.

    Returns:
        A non-negative value. Sentence-ending periods, question marks, and
        exclamation marks are excluded.
    """
    token_count = len(words(text))
    if token_count == 0:
        return 0.0
    marks = sum(char in ",;:—–-()[]" for char in text)
    return marks / token_count


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    Lower sentence spread, lower vocabulary variety, and less non-terminal
    punctuation each contribute a higher AI-like component. Each component is
    normalized to 0–1 before averaging. These heuristics are sensitive to text
    length and editing; they do not establish authorship.
    """
    if not words(text):
        return 0.5

    spread_ai = 1.0 - min(sentence_length_spread(text), 1.0)
    vocabulary_ai = 1.0 - type_token_ratio(text)
    punctuation_ai = 1.0 - min(punctuation_density(text) / 0.12, 1.0)

    return round((spread_ai + vocabulary_ai + punctuation_ai) / 3.0, 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
