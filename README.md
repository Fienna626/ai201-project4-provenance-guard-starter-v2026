# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. A client sends `text` and `creator_id` as JSON to `POST /submit`.
2. The route validates that both are non-empty strings, rejects text over
   10,000 characters, and reports text that is too short for the detector.
3. `detector.model_signal` scores how predictable the text is to the local
   language model.
4. `stylometry.style_signal` scores sentence-length variation, vocabulary
   repetition, and selected punctuation patterns.
5. `scoring.combine_signals` averages the two scores using the configured
   weights: 0.50 model and 0.50 style. The combined score is returned as both
   `combined_score` and `confidence`; it is not a calibrated probability.
6. The route creates a `content_id`, writes the decision and both component
   scores plus the combined score to `logs/audit.jsonl`, and returns the scores.
7. **Current milestone status:** the response's `guess` and `label` are still
   pending. Milestone 5's score-to-label mapping and the appeal handler have
   not yet been implemented.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** `detector.model_signal` scores how predictable the text is
to the local GPT-2 model; lower perplexity becomes a higher 0–1 score.

**Why that might differ between human and AI writing:** Generated text often
uses likely next words, while human writing can be more surprising.

**What it can't see:** Predictability is not authorship. Plain, conventional
human writing may also be predictable, and unusual human writing can look
surprising to the model.

### Signal two — the style signal

**What it measures:** `stylometry.style_signal` averages three normalized
heuristics: inverse sentence-length variation, inverse type-token ratio, and
inverse density of commas, semicolons, colons, dashes, and brackets. Each
component and the final score are on a 0–1 scale; higher means more AI-like.
Specifically, sentence variation is capped at a coefficient of variation of
`1.0`, and punctuation density is scaled to `0–1` over `0.12` marks per word;
the type-token ratio is already between `0` and `1`.

**Why that might differ between human and AI writing:** Generated prose may
have more even sentence lengths, repeated vocabulary, and fewer unusual
non-terminal punctuation marks than an individual writer's text.

**What it can't see:** It cannot understand meaning or verify authorship.
Sentence splitting, quotations, and punctuation edits can change the features
without changing who wrote the underlying ideas. Type-token ratio also varies
with text length.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** Take the weighted arithmetic mean of the two 0–1 scores, rounded
to four decimal places. A disagreement pulls the result between the signals,
toward uncertainty, rather than allowing one score to override the other.

**The numbers:** `0.50 × model_score + 0.50 × style_score`. The current
thresholds are `0.35` and `0.65`; scores between them will be the unsure band
when label mapping is implemented in Milestone 5. The API's `confidence` field
currently carries this combined AI-likelihood score; it is not a probability
that the authorship decision is correct.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** On the
AI-written polished sample, the model signal was `0.0802` while the style
signal was `0.4873`. Their equal-weight average is `0.2838`, so one near-neutral
style signal does not override the model's low score. This is a miss for that
AI-written sample, not evidence that the score proves authorship. On the
conventional borderline sample, the signals were `0.6145` and `0.4372`; the
combined `0.5259` lands between them instead of treating the model signal
alone as decisive.

Calibration runs used the same signal implementations on these five
deliberately composed samples. The AI-written examples were generated for this
check; the personal and formal examples are style stand-ins, not independently
verified human-authored data.

| Sample | Model signal | Style signal | Combined score |
|---|---:|---:|---:|
| AI-written polished prose | 0.0802 | 0.4873 | 0.2838 |
| Personal narrative style | 0.2971 | 0.4745 | 0.3858 |
| Conventional borderline prose | 0.6145 | 0.4372 | 0.5259 |
| Formal prose style | 0.1776 | 0.3389 | 0.2583 |
| Lightly edited AI-written prose | 0.3721 | 0.2603 | 0.3162 |



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and its audit log entry, pasted as text: the request,
     response, and log entry. -->

**A submission**

<!-- confidence is the combined AI-likelihood score, not calibrated certainty.
     The guess and reader-facing label remain pending until Milestone 5. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "The narrow street was wet from the storm. I stopped to tie my shoe, then noticed a small blue button in the gutter.", "creator_id": "milestone4-demo"}'
```

```json
{
  "combined_score": 0.4545,
  "confidence": 0.4545,
  "content_id": "3c54b1bb-2d23-49bf-928e-b1fc647d0c46",
  "creator_id": "milestone4-demo",
  "guess": "pending",
  "label": "Pending label mapping.",
  "model_score": 0.4775,
  "style_score": 0.4314
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=1"
```

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": 0.4545,
      "content_id": "3c54b1bb-2d23-49bf-928e-b1fc647d0c46",
      "creator_id": "milestone4-demo",
      "guess": "pending",
      "label": "Pending label mapping.",
      "model_score": 0.4775,
      "status": "decided",
      "style_score": 0.4314,
      "timestamp": "2026-10-25T07:57:36+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked the AI to trace a submission through the starter
  service, explain what each signal measures and cannot see, and describe the
  false-positive and endpoint-contract paths.
- *What came back:* It inspected `app.py`, `detector.py`, `stylometry.py`,
  `scoring.py`, and `audit.py`, then returned a seven-step flow and identified
  that `/submit` and `/appeal` were still starter stubs.
- *What I changed:* I used that trace to write five measurable acceptance
  criteria in `criteria.md`, including a false-positive limit, appeal behavior,
  and malformed-input behavior.

**Moment 2**

- *What I asked for:* I asked the AI to implement Milestones 3 and 4: first
  verify a hardcoded route, then add the local-model signal, implement the
  style features and combining rule, and check the response and audit log.
- *What came back:* It implemented the staged endpoint and three stylometry
  measures, used an equal-weight average, and ran sample inputs through both
  signals. The polished AI-style sample notably scored 0.0802 on the model
  signal and 0.4873 on the style signal.
- *What I changed:* I kept equal weights so neither imperfect heuristic
  dominates, checked the values against the endpoint and audit output, and
  documented the AI-style sample as a miss rather than presenting the detector
  as reliable authorship proof.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
