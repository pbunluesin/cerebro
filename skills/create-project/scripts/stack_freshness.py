#!/usr/bin/env python3
"""Shared fail-closed Stack Pack freshness evaluation."""

from __future__ import annotations

import datetime as dt
from typing import Iterable


def parse_date(value: object, label: str) -> dt.date:
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{label} has invalid ISO date {value!r}") from exc


def evaluate_freshness(
    as_of: dt.date,
    policy: dict,
    catalog: dict,
    selected_scopes: Iterable[str] | None = None,
) -> dict:
    selected = (
        set(selected_scopes)
        if selected_scopes is not None
        else set(catalog.get("stacks", {}))
    )
    deadlines: list[dict] = [
        {
            "kind": "version-policy",
            "label": "version policy",
            "date": parse_date(
                policy.get("next_review_at"),
                "version policy",
            ),
        },
        {
            "kind": "light-source-review",
            "label": "official source catalog light review",
            "date": parse_date(
                catalog.get("next_light_review_at"),
                "official source catalog light review",
            ),
        },
        {
            "kind": "full-semantic-review",
            "label": "official source catalog full semantic review",
            "date": parse_date(
                catalog.get("next_full_review_at"),
                "official source catalog full semantic review",
            ),
        },
    ]
    for scope in sorted(selected):
        source = catalog.get("stacks", {}).get(scope, {})
        for field, label in (
            ("house_standards", "house standard"),
            ("engineering_guides", "engineering guide"),
        ):
            for reference in source.get(field, []):
                reference_id = reference.get("id")
                deadlines.append(
                    {
                        "kind": field,
                        "label": f"{scope} {label} {reference_id}",
                        "date": parse_date(
                            reference.get("next_review_at"),
                            f"{scope} {label} {reference_id}",
                        ),
                    }
                )

    overdue = [item for item in deadlines if as_of > item["date"]]
    status = "current"
    if overdue:
        status = (
            "full-review-due"
            if all(
                item["kind"] == "full-semantic-review"
                for item in overdue
            )
            else "stale"
        )
    return {
        "status": status,
        "deadlines": deadlines,
        "overdue": overdue,
    }
