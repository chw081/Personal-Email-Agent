# Email Analysis Evaluation

This folder contains the evaluation dataset and runner for the email analysis pipeline. It is **not** part of the unit-test suite — it calls the real analysis provider (LLM or rule-based) and measures output quality against hand-labelled ground truth.

---

## Quick start

```bash
# From backend/, with the virtual environment active:

# Evaluate whichever provider is set in .env (ANALYSIS_PROVIDER)
python evals/run_evals.py

# Override to a specific provider
python evals/run_evals.py --provider rule_based
python evals/run_evals.py --provider llm

# Use a different dataset file
python evals/run_evals.py --dataset evals/my_dataset.json
```

> **LLM runs cost API calls.** Each sample is one `generate_content` call. With `gemini-2.5-flash` the cost is minimal, but be aware when running large datasets.

---

## Files

| File | Purpose |
|------|---------|
| `dataset.json` | Ground-truth evaluation samples |
| `run_evals.py` | Evaluation runner — loads dataset, calls provider, prints report |
| `README.md` | This file |

---

## Output

```
════════════════════════════════════════════════════════════════════════════════
  Evaluation report — LLMEmailAnalysisProvider
════════════════════════════════════════════════════════════════════════════════

  Samples total      : 12
  Errors / skipped   : 0
  Scored             : 12

  Priority accuracy  :   83%  (10/12)
  Category accuracy  :  100%  (12/12)
  Action item hit    :   91%  (11/12)
  Overall pass rate  :   83%  (10/12)

────────────────────────────────────────────────────────────────────────────────
  FAILURES  (priority or category mismatch)
  ...

────────────────────────────────────────────────────────────────────────────────
  PER-SAMPLE RESULTS
  ✓  career-001      priority=High  category=Career      Interview invitation...
  ...
```

The runner exits with code `0` if all samples pass, `1` if any fail — useful for CI gates.

---

## Dataset format

`dataset.json` is a JSON array. Each entry has:

```json
{
  "_id": "unique-id",
  "_note": "Human note describing the test case",
  "input": {
    "subject": "...",
    "sender": "...",
    "snippet": "...",
    "body": "..." or null
  },
  "expected": {
    "priority": "High | Medium | Low",
    "category": "Career | Finance | Promotion | Other",
    "action_items_contain": ["keyword1", "keyword2"]
  }
}
```

### Field notes

- `_id` — unique string; used in failure output. Convention: `{category}-{nnn}`.
- `_note` — human-readable description; not used in scoring.
- `body` — can be `null` to simulate snippet-only emails.
- `action_items_contain` — a list of keywords; the test passes if **any one** appears in the predicted action items (case-insensitive). Use `[]` when you do not want to assert on action items.

### Scoring rules

| Metric | Method |
|--------|--------|
| **Priority accuracy** | Exact string match (`"High"`, `"Medium"`, `"Low"`) |
| **Category accuracy** | Exact string match (`"Career"`, `"Finance"`, `"Promotion"`, `"Other"`) |
| **Action item hit rate** | At least one `action_items_contain` keyword found in the predicted items (soft match) |
| **Overall pass rate** | Priority **and** category both match |

`summary` is intentionally not scored — free-form generation is not meaningfully comparable with string equality.

---

## Adding samples

1. Open `dataset.json`.
2. Append a new JSON object following the format above.
3. Give it a unique `_id` and a descriptive `_note`.
4. Set `expected.priority` and `expected.category` to what you believe the correct answer is.
5. Add keywords to `expected.action_items_contain` if you want to assert on action quality (optional).
6. Run `python evals/run_evals.py` to confirm the new case behaves as expected.

Good sample diversity to aim for:
- Edge cases (e.g. a promotional email that mentions a deadline — should it be Low or High?)
- Ambiguous subjects where body content changes the answer
- Snippet-only vs body-available comparisons of the same email
- Emails that could plausibly fit two categories

---

## Comparing providers

Run both providers and compare the printed metrics:

```bash
python evals/run_evals.py --provider rule_based 2>&1 | tee eval_rule_based.txt
python evals/run_evals.py --provider llm        2>&1 | tee eval_llm.txt
diff eval_rule_based.txt eval_llm.txt
```

---

## What this is not

- **Not a unit test** — do not run this with `python -m unittest discover`. It calls real providers and may make external API calls.
- **Not a training loop** — nothing is fine-tuned. Results only inform prompt or provider changes.
- **Not exhaustive** — 12 samples is a starting point. Accuracy numbers are directional, not statistically rigorous.
