"""
Email analysis evaluation runner.

Evaluates the configured analysis provider against a ground-truth dataset.
Separate from the unit-test suite: this calls the real provider (LLM or
rule-based) and reports quality metrics — priority accuracy, category
accuracy, action-item hit rate, classification pass rate, and strict pass rate.

Pass metric definitions
  classification_pass  priority AND category both match
  strict_pass          priority AND category AND action item hit all pass

Usage (from backend/):
    python evals/run_evals.py                        # uses ANALYSIS_PROVIDER from .env
    python evals/run_evals.py --provider rule_based  # override provider
    python evals/run_evals.py --provider llm         # override provider
    python evals/run_evals.py --dataset evals/dataset.json  # custom dataset path
    python evals/run_evals.py --fail-on-mismatch     # exit 1 on any classification failure (CI)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Allow running from backend/ without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.schemas.analysis import EmailAnalysisRequest, EmailAnalysisResponse
from app.services.analysis_providers.base import EmailAnalysisProvider
from app.services.analysis_providers.llm import LLMEmailAnalysisProvider
from app.services.analysis_providers.rule_based import RuleBasedEmailAnalysisProvider

DATASET_PATH = Path(__file__).parent / "dataset.json"

# Column widths for the failure table
_COL_ID = 12
_COL_FIELD = 10
_COL_EXPECTED = 12
_COL_PREDICTED = 12
_COL_SUBJECT = 38


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class EvalSample:
    id: str
    note: str
    input: EmailAnalysisRequest
    expected_priority: str
    expected_category: str
    action_items_contain: list[str]   # any one keyword must appear in predicted items


@dataclass
class EvalResult:
    sample: EvalSample
    predicted: EmailAnalysisResponse | None
    error: str | None = None

    @property
    def priority_match(self) -> bool:
        return self.predicted is not None and self.predicted.priority == self.sample.expected_priority

    @property
    def category_match(self) -> bool:
        return self.predicted is not None and self.predicted.category == self.sample.expected_category

    @property
    def action_item_hit(self) -> bool:
        """True if the sample has no keyword requirements OR at least one keyword appears."""
        if not self.sample.action_items_contain:
            return True
        if self.predicted is None:
            return False
        predicted_text = " ".join(self.predicted.action_items).lower()
        return any(kw.lower() in predicted_text for kw in self.sample.action_items_contain)

    @property
    def classification_pass(self) -> bool:
        """Priority AND category both match."""
        return self.priority_match and self.category_match

    @property
    def strict_pass(self) -> bool:
        """Priority AND category AND action item hit all pass."""
        return self.classification_pass and self.action_item_hit


@dataclass
class EvalReport:
    provider_name: str
    results: list[EvalResult] = field(default_factory=list)

    # --- aggregate helpers ---

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def errored(self) -> int:
        return sum(1 for r in self.results if r.error)

    @property
    def scored(self) -> int:
        return self.total - self.errored

    def _pct(self, count: int) -> str:
        if self.scored == 0:
            return "n/a"
        return f"{count / self.scored * 100:.0f}%"

    @property
    def priority_correct(self) -> int:
        return sum(1 for r in self.results if r.priority_match)

    @property
    def category_correct(self) -> int:
        return sum(1 for r in self.results if r.category_match)

    @property
    def action_item_hits(self) -> int:
        return sum(1 for r in self.results if r.action_item_hit)

    @property
    def classification_passed(self) -> int:
        return sum(1 for r in self.results if r.classification_pass)

    @property
    def strict_passed(self) -> int:
        return sum(1 for r in self.results if r.strict_pass)

    def priority_accuracy(self) -> str:
        return self._pct(self.priority_correct)

    def category_accuracy(self) -> str:
        return self._pct(self.category_correct)

    def action_item_hit_rate(self) -> str:
        return self._pct(self.action_item_hits)

    def classification_pass_rate(self) -> str:
        return self._pct(self.classification_passed)

    def strict_pass_rate(self) -> str:
        return self._pct(self.strict_passed)


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------

def load_dataset(path: Path) -> list[EvalSample]:
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    samples: list[EvalSample] = []
    for entry in raw:
        samples.append(
            EvalSample(
                id=entry["_id"],
                note=entry.get("_note", ""),
                input=EmailAnalysisRequest.model_validate(entry["input"]),
                expected_priority=entry["expected"]["priority"],
                expected_category=entry["expected"]["category"],
                action_items_contain=entry["expected"].get("action_items_contain", []),
            )
        )
    return samples


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

def build_provider(provider_name: str) -> EmailAnalysisProvider:
    name = provider_name.strip().lower()
    if name == "llm":
        return LLMEmailAnalysisProvider()
    if name == "rule_based":
        return RuleBasedEmailAnalysisProvider()
    raise ValueError(f"Unknown provider '{provider_name}'. Choose 'llm' or 'rule_based'.")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_evals(provider: EmailAnalysisProvider, samples: list[EvalSample]) -> EvalReport:
    provider_name = type(provider).__name__
    report = EvalReport(provider_name=provider_name)

    for sample in samples:
        try:
            predicted = provider.analyze(sample.input)
            report.results.append(EvalResult(sample=sample, predicted=predicted))
        except Exception as exc:  # noqa: BLE001
            report.results.append(EvalResult(sample=sample, predicted=None, error=str(exc)))

    return report


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _divider(char: str = "─", width: int = 80) -> str:
    return char * width


def _truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def print_report(report: EvalReport) -> None:
    print()
    print(_divider("═"))
    print(f"  Evaluation report — {report.provider_name}")
    print(_divider("═"))

    # Summary table
    print()
    print(f"  Samples total        : {report.total}")
    print(f"  Errors / skipped     : {report.errored}")
    print(f"  Scored               : {report.scored}")
    print()
    print(f"  Priority accuracy    : {report.priority_accuracy():>5}  ({report.priority_correct}/{report.scored})")
    print(f"  Category accuracy    : {report.category_accuracy():>5}  ({report.category_correct}/{report.scored})")
    print(f"  Action item hit rate : {report.action_item_hit_rate():>5}  ({report.action_item_hits}/{report.scored})")
    print()
    print(f"  Classification pass  : {report.classification_pass_rate():>5}  ({report.classification_passed}/{report.scored})  priority + category")
    print(f"  Strict pass          : {report.strict_pass_rate():>5}  ({report.strict_passed}/{report.scored})  priority + category + action items")
    print()

    # Errors
    errors = [r for r in report.results if r.error]
    if errors:
        print(_divider())
        print("  ERRORS")
        print(_divider())
        for r in errors:
            print(f"  [{r.sample.id}] {r.error}")
        print()

    # Classification failures (priority or category mismatch)
    failures = [r for r in report.results if not r.classification_pass and not r.error]
    if failures:
        print(_divider())
        print("  CLASSIFICATION FAILURES  (priority or category mismatch)")
        print(_divider())
        header = (
            f"  {'ID':<{_COL_ID}} {'Field':<{_COL_FIELD}} "
            f"{'Expected':<{_COL_EXPECTED}} {'Got':<{_COL_PREDICTED}} "
            f"Subject"
        )
        print(header)
        print("  " + "·" * (_COL_ID + _COL_FIELD + _COL_EXPECTED + _COL_PREDICTED + _COL_SUBJECT + 8))
        for r in failures:
            subject = _truncate(r.sample.input.subject, _COL_SUBJECT)
            sid = _truncate(r.sample.id, _COL_ID)
            if not r.priority_match:
                print(
                    f"  {sid:<{_COL_ID}} {'priority':<{_COL_FIELD}} "
                    f"{r.sample.expected_priority:<{_COL_EXPECTED}} "
                    f"{(r.predicted.priority if r.predicted else 'n/a'):<{_COL_PREDICTED}} "
                    f"{subject}"
                )
            if not r.category_match:
                print(
                    f"  {sid:<{_COL_ID}} {'category':<{_COL_FIELD}} "
                    f"{r.sample.expected_category:<{_COL_EXPECTED}} "
                    f"{(r.predicted.category if r.predicted else 'n/a'):<{_COL_PREDICTED}} "
                    f"{subject}"
                )
        print()

    # Action item misses (counted in strict_pass but not classification_pass)
    action_misses = [
        r for r in report.results
        if not r.action_item_hit and not r.error and r.sample.action_items_contain
    ]
    if action_misses:
        print(_divider())
        print("  ACTION ITEM MISSES  (fails strict pass; does not affect classification pass)")
        print(_divider())
        for r in action_misses:
            predicted_items = r.predicted.action_items if r.predicted else []
            print(f"  [{r.sample.id}]  {_truncate(r.sample.input.subject, 60)}")
            print(f"    expected (any of) : {r.sample.action_items_contain}")
            if predicted_items:
                for i, item in enumerate(predicted_items, 1):
                    print(f"    predicted [{i}]     : {item}")
            else:
                print( "    predicted         : (no action items returned)")
            print()

    # Per-sample detail
    print(_divider())
    print("  PER-SAMPLE RESULTS")
    print(_divider())
    for r in report.results:
        if r.error:
            status = "ERR"
        elif r.strict_pass:
            status = "✓✓"   # classification + action items
        elif r.classification_pass:
            status = "✓ "   # classification only (action item miss)
        else:
            status = "✗ "   # classification failure

        if r.predicted:
            detail = f"priority={r.predicted.priority}  category={r.predicted.category}"
        elif r.error:
            detail = f"error: {_truncate(r.error, 50)}"
        else:
            detail = "no prediction"
        subject = _truncate(r.sample.input.subject, 45)
        print(f"  {status}  {r.sample.id:<14}  {detail:<36}  {subject}")

    print()
    print("  ✓✓ = strict pass   ✓  = classification pass (action item miss)   ✗  = classification failure")
    print()
    print(_divider("═"))
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate email analysis provider quality against a ground-truth dataset."
    )
    parser.add_argument(
        "--provider",
        default=None,
        choices=["llm", "rule_based"],
        help="Override ANALYSIS_PROVIDER from .env (default: use configured value)",
    )
    parser.add_argument(
        "--dataset",
        default=str(DATASET_PATH),
        help=f"Path to evaluation dataset JSON (default: {DATASET_PATH})",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        default=False,
        help="Exit with code 1 if any classification failure occurs (useful for CI gates)",
    )
    args = parser.parse_args()

    # Resolve provider
    provider_name = args.provider or get_settings().analysis_provider
    print(f"\nLoading provider: {provider_name}")
    try:
        provider = build_provider(provider_name)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}", file=sys.stderr)
        sys.exit(1)
    samples = load_dataset(dataset_path)
    print(f"Loaded {len(samples)} samples from {dataset_path}")

    # Run
    report = run_evals(provider, samples)
    print_report(report)

    # Exit 1 only when explicitly requested (e.g. CI)
    if args.fail_on_mismatch and report.classification_passed < report.scored:
        sys.exit(1)


if __name__ == "__main__":
    main()
