"""Top-pageviews discovery via the Wikimedia REST API."""

from __future__ import annotations

import datetime as _dt
import time


def fetch_top_pageviews(
    limit: int,
    timeframe: str,
    rest_base_url: str,
    session,
    min_pageviews: int = 0,
    timeout: int = 30,
    max_retries: int = 3,
    rate_limit_sleep: float = 0.0,
) -> list[tuple[str, int]]:
    """Return ``(title, views)`` pairs ranked by aggregated views, descending."""
    counts: dict[str, int] = {}
    for day in _day_list(timeframe):
        url = (
            f"{rest_base_url}/metrics/pageviews/top/en.wikipedia/all-access/"
            f"{day.year}/{day.month:02d}/{day.day:02d}"
        )
        data = _get_json(session, url, timeout, max_retries)
        for item in data.get("items") or []:
            for article in item.get("articles") or []:
                title = article.get("article")
                views = int(article.get("views", 0))
                if title is not None and views >= min_pageviews:
                    counts[title] = counts.get(title, 0) + views
        if rate_limit_sleep:
            time.sleep(rate_limit_sleep)

    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return ranked[:limit]


def _day_list(timeframe: str) -> list[_dt.date]:
    today = _dt.date.today()
    if timeframe == "last-day":
        return [today - _dt.timedelta(days=1)]
    # "last-month": the previous 30 complete days.
    return [today - _dt.timedelta(days=i + 1) for i in range(30)]


def _get_json(session, url, timeout, max_retries):
    for _attempt in range(max_retries + 1):
        response = session.get(url, timeout=timeout)
        if response.status_code == 429:
            time.sleep(float(response.headers.get("retry-after", 5)))
            continue
        if response.status_code == 404:
            # The "top" endpoint 404s for days whose data isn't published yet
            # (e.g. the most recent day, or a mis-set system clock). Treat it
            # as "no data for this day" rather than a fatal error.
            return {"items": []}
        response.raise_for_status()
        return response.json()
    raise RuntimeError(f"pageviews: giving up after {max_retries} retries")