# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

Of 10 pieces of writing I authored myself, no more than 1 may receive the
high-confidence AI label in **each of the three evaluation trials**.

**Why this target:**

False accusations can harm a real writer more than a missed AI submission
harms the site. Requiring the limit in every trial keeps a lucky run from
hiding an inconsistent detector.

---

## 2.

For a fixed set of 5 clearly human-written and 5 clearly AI-written samples,
the mean combined score for the AI-written set must exceed the human-written
set by at least **0.20 in each of the three evaluation trials**.

**Why this target:**

The score should provide a useful distinction across known examples, not just
produce different labels by chance. A 0.20 gap is a meaningful, checkable
separation while recognizing that these scores are estimates, not proof.

---

## 3.

Each of the three labels—`human`, `unsure`, and `ai`—must be returned by at
least **one sample in the fixed 10-sample evaluation set in each trial**.

**Why this target:**

All three outcomes need to be reachable for the service to express uncertainty
as well as strong judgments. Checking each trial catches label coverage that
depends on a one-off score fluctuation.

---

## 4.

For an existing `content_id`, a valid appeal must return a successful response
and append **exactly one** appeal event with that ID and status `under_review`.
An appeal for an unknown ID must return a 4xx response and append **no** appeal
event.

**Why this target:**

The writer needs a verifiable path to challenge a decision, and a typo or
unknown ID should not look like a successful appeal. Checking the response and
append-only log makes both outcomes observable.

---

## 5.

Requests with missing `text`, non-string `text`, whitespace-only `text`, or
more than **10,000 characters** must each return a JSON 4xx error, create no
decision entry, and never produce a server error. Each rejected request must
also create one rejection entry in the audit log.

**Why this target:**

These inputs are malformed or unnecessarily large and should not reach the
signals or crash the route. A defined size bound and visible rejection make
the behavior testable and help diagnose rejected submissions.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
