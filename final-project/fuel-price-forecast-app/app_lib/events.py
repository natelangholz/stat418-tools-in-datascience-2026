"""Curated U.S. gasoline market context: shocks, peaks, and lows.

Chart markers snap to the nearest EIA week, or to a local high/low near the
listed date for peak/trough entries. For illustration only — not causal inference.
"""

from __future__ import annotations

from typing import Literal, TypedDict

import pandas as pd

EventKind = Literal["event", "peak", "trough"]
EventScope = Literal["us", "international"]


class MarketEvent(TypedDict):
    date: str
    kind: EventKind
    scope: EventScope
    title: str  # short label on chart
    detail: str  # plain-English hover text


# kind: event = news/shock   peak = local high   trough = local low
# scope: us = mainly U.S. policy/supply   international = global oil & geopolitics

EVENTS: list[MarketEvent] = [
    # —— U.S. supply & infrastructure ——
    {
        "date": "2005-08-29",
        "kind": "event",
        "scope": "us",
        "title": "Hurricane Katrina",
        "detail": "U.S. Gulf Coast: refineries and pipelines damaged → regional gasoline shortages and price spikes.",
    },
    {
        "date": "2017-08-25",
        "kind": "event",
        "scope": "us",
        "title": "Hurricane Harvey",
        "detail": "Texas/Louisiana refineries shut → ~25% of U.S. refining offline; pump prices jumped in the South and East.",
    },
    {
        "date": "2021-05-07",
        "kind": "event",
        "scope": "us",
        "title": "Colonial Pipeline shutdown",
        "detail": "Cyberattack stopped main East Coast fuel pipeline → panic buying; Southeast retail prices surged temporarily.",
    },
    # —— Global / financial / geopolitical ——
    {
        "date": "2008-09-15",
        "kind": "event",
        "scope": "international",
        "title": "Lehman bankruptcy (GFC)",
        "detail": "Global financial crisis deepens → oil demand fears; extreme volatility in crude and gasoline.",
    },
    {
        "date": "2011-02-24",
        "kind": "event",
        "scope": "international",
        "title": "Libya civil war begins",
        "detail": "Libyan oil exports disrupted during Arab Spring → global crude risk premium; U.S. pump prices rose toward $4/gal.",
    },
    {
        "date": "2014-11-27",
        "kind": "event",
        "scope": "international",
        "title": "OPEC keeps output high",
        "detail": "OPEC (Thanksgiving meeting) defends market share instead of cutting → crude collapsed; years of cheaper gasoline followed.",
    },
    {
        "date": "2020-03-11",
        "kind": "event",
        "scope": "international",
        "title": "COVID-19 pandemic declared",
        "detail": "WHO pandemic declaration → lockdowns worldwide; driving and jet fuel demand collapsed.",
    },
    {
        "date": "2020-04-20",
        "kind": "event",
        "scope": "international",
        "title": "WTI futures turn negative",
        "detail": "May WTI contract settled below $0 → Cushing storage full; symbol of the 2020 oil demand crash (gasoline fell too).",
    },
    {
        "date": "2022-02-24",
        "kind": "event",
        "scope": "international",
        "title": "Russia invades Ukraine",
        "detail": "War + sanctions on Russian energy → global crude spike; Western countries sought alternative supply; pump prices surged.",
    },
    {
        "date": "2023-04-02",
        "kind": "event",
        "scope": "international",
        "title": "OPEC+ surprise output cut",
        "detail": "Saudi-led OPEC+ announced extra voluntary cuts → Brent rose; supported gasoline from spring lows.",
    },
    {
        "date": "2023-10-07",
        "kind": "event",
        "scope": "international",
        "title": "Israel–Hamas war outbreak",
        "detail": "Middle East conflict fears → oil risk premium; gasoline volatility even without large immediate supply loss.",
    },
    # —— Major price peaks (national weekly series context) ——
    {
        "date": "2008-07-14",
        "kind": "peak",
        "scope": "international",
        "title": "Peak ~$4.11 (Jul 2008)",
        "detail": "Summer 2008: crude oil neared $147/bbl; U.S. weekly retail gasoline reached an all-time nominal high before the GFC crash.",
    },
    {
        "date": "2011-05-09",
        "kind": "peak",
        "scope": "international",
        "title": "Peak ~$3.91 (May 2011)",
        "detail": "Arab Spring + Libya outage fears kept global oil tight; U.S. average gasoline approached $4/gal again.",
    },
    {
        "date": "2014-05-26",
        "kind": "peak",
        "scope": "international",
        "title": "Peak ~$3.71 (May 2014)",
        "detail": "Last elevated spring before the 2014–2016 oil glut; prices fell sharply after OPEC’s market-share strategy.",
    },
    {
        "date": "2022-06-13",
        "kind": "peak",
        "scope": "international",
        "title": "Peak ~$5.11 (Jun 2022)",
        "detail": "Post-Ukraine invasion summer: record nominal U.S. weekly average; refining margins and crude both very high.",
    },
    {
        "date": "2025-04-14",
        "kind": "peak",
        "scope": "international",
        "title": "Recent high (2025)",
        "detail": "Elevated spring 2025 levels in EIA data — tighter markets and seasonal demand (exact drivers vary by year).",
    },
    # —— Major price lows ——
    {
        "date": "2009-01-05",
        "kind": "trough",
        "scope": "international",
        "title": "Low ~$1.78 (Jan 2009)",
        "detail": "After Lehman: global recession crushed oil demand; U.S. gasoline fell from the 2008 peak to multiyear lows.",
    },
    {
        "date": "2016-02-15",
        "kind": "trough",
        "scope": "international",
        "title": "Low ~$1.72 (Feb 2016)",
        "detail": "Oil glut bottom: U.S. shale boom + OPEC oversupply; crude under $30/bbl; cheap gasoline for consumers.",
    },
    {
        "date": "2020-04-27",
        "kind": "trough",
        "scope": "international",
        "title": "Low ~$1.77 (Apr 2020)",
        "detail": "COVID lockdown trough: U.S. driving collapsed; among the lowest national averages of the past 20 years.",
    },
    {
        "date": "2023-12-18",
        "kind": "trough",
        "scope": "international",
        "title": "Low ~$3.05 (Dec 2023)",
        "detail": "Late-2023 easing: softer crude, seasonal winter demand lull; relief from 2022 highs.",
    },
]


def snap_to_series(raw: pd.DataFrame, ev: MarketEvent) -> pd.Series | None:
    """Place marker on nearest week, or on local max/min within ±12 weeks for peaks/troughs."""
    tmin, tmax = raw["period"].min(), raw["period"].max()
    ed = pd.Timestamp(ev["date"])
    if ed < tmin - pd.Timedelta(weeks=52) or ed > tmax + pd.Timedelta(weeks=52):
        return None

    window = raw.loc[
        (raw["period"] >= ed - pd.Timedelta(weeks=12))
        & (raw["period"] <= ed + pd.Timedelta(weeks=12))
    ]
    if ev["kind"] == "peak" and len(window) > 0:
        return window.loc[window["price"].idxmax()]
    if ev["kind"] == "trough" and len(window) > 0:
        return window.loc[window["price"].idxmin()]

    j = int((raw["period"] - ed).abs().values.argmin())
    return raw.iloc[j]


def events_for_chart(raw: pd.DataFrame) -> list[tuple[MarketEvent, pd.Series]]:
    out: list[tuple[MarketEvent, pd.Series]] = []
    for ev in EVENTS:
        row = snap_to_series(raw, ev)
        if row is not None:
            out.append((ev, row))
    return out


def scope_label(scope: EventScope) -> str:
    return "U.S." if scope == "us" else "Global"


def kind_label(kind: EventKind) -> str:
    return {"event": "News / shock", "peak": "Price peak", "trough": "Price low"}[kind]
