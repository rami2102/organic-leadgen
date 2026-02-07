"""Generate a content calendar from keyword research."""

from dataclasses import dataclass
from datetime import date, timedelta


NICHES = [
    "restaurants",
    "law firms",
    "real estate",
    "dental offices",
    "hvac plumbing",
    "accounting firms",
]


@dataclass
class CalendarEntry:
    publish_date: date
    niche: str
    keyword: str
    search_volume: int
    post_type: str  # "how-to", "listicle", "case-study", "comparison"


def generate_calendar(
    keywords_by_niche: dict[str, list[dict]],
    start_date: date,
    posts_per_week: int = 3,
) -> list[CalendarEntry]:
    """Generate a publishing calendar rotating through niches.

    Posts 3x/week by default, rotating niches to cover all verticals.
    Prioritizes low-competition, high-volume keywords.
    """
    entries = []
    day = start_date
    post_types = ["how-to", "listicle", "case-study", "comparison"]
    niche_index = 0
    type_index = 0

    week_count = 0
    while week_count < 4:  # 4 weeks = 1 month
        for _ in range(posts_per_week):
            niche = NICHES[niche_index % len(NICHES)]
            niche_keywords = keywords_by_niche.get(niche, [])

            if niche_keywords:
                kw = niche_keywords.pop(0)
                entries.append(
                    CalendarEntry(
                        publish_date=day,
                        niche=niche,
                        keyword=kw["keyword"],
                        search_volume=kw["search_volume"],
                        post_type=post_types[type_index % len(post_types)],
                    )
                )
                type_index += 1

            niche_index += 1
            day += timedelta(days=2)  # Every other day

        week_count += 1
        # Skip to next week if needed
        while day.weekday() >= 5:  # Skip weekends
            day += timedelta(days=1)

    return entries
