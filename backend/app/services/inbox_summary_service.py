"""Inbox-level summary from analyzed email results."""

from collections import Counter

from app.schemas.analysis import AnalyzedEmail, InboxSummaryResponse

EMPTY_INBOX_SUMMARY = "No emails to summarize."
PRIORITY_ORDER = ("High", "Medium", "Low")
TOP_CATEGORY_COUNT = 2


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _format_priority_phrase(count: int, priority: str) -> str:
    return f"{count} {priority.lower()} priority"


def _join_phrases(phrases: list[str]) -> str:
    if not phrases:
        return ""
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]} and {phrases[1]}"
    return ", ".join(phrases[:-1]) + f", and {phrases[-1]}"


def _build_summary_text(
    total_emails: int,
    priority_counts: dict[str, int],
    category_counts: dict[str, int],
) -> str:
    if total_emails == 0:
        return EMPTY_INBOX_SUMMARY

    priority_phrases = [
        _format_priority_phrase(priority_counts[priority], priority)
        for priority in PRIORITY_ORDER
        if priority_counts.get(priority, 0) > 0
    ]

    sorted_categories = sorted(
        category_counts.items(),
        key=lambda item: (-item[1], item[0]),
    )
    top_categories = [name for name, count in sorted_categories[:TOP_CATEGORY_COUNT] if count > 0]

    email_word = "email" if total_emails == 1 else "emails"
    summary = f"You have {total_emails} {email_word}: {_join_phrases(priority_phrases)}."

    if len(top_categories) == 1:
        summary += f" Top category is {top_categories[0]}."
    elif len(top_categories) == 2:
        summary += f" Top categories are {top_categories[0]} and {top_categories[1]}."

    return summary


def summarize_analyzed_emails(results: list[AnalyzedEmail]) -> InboxSummaryResponse:
    """Build an inbox summary from previously analyzed email results."""
    if not results:
        return InboxSummaryResponse(
            total_emails=0,
            priority_counts={},
            category_counts={},
            top_action_items=[],
            summary=EMPTY_INBOX_SUMMARY,
        )

    priority_counts = dict(Counter(result.analysis.priority for result in results))
    category_counts = dict(Counter(result.analysis.category for result in results))
    action_items = _dedupe_preserve_order(
        item for result in results for item in result.analysis.action_items
    )

    return InboxSummaryResponse(
        total_emails=len(results),
        priority_counts=priority_counts,
        category_counts=category_counts,
        top_action_items=action_items,
        summary=_build_summary_text(len(results), priority_counts, category_counts),
    )
