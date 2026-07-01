"""Mock research provider for local development and testing."""

from datetime import UTC, datetime, timedelta

from app.services.research.base_provider import BaseResearchProvider
from app.services.research.models import ResearchQuery, ResearchResult, ResearchSource


class MockResearchProvider(BaseResearchProvider):
    """Returns synthetic research sources without external network calls."""

    @property
    def name(self) -> str:
        return "mock"

    def search(self, query: ResearchQuery) -> ResearchResult:
        slug = query.query.lower().replace(" ", "-")
        now = datetime.now(UTC)

        templates = [
            (
                f"How {query.query} is reshaping short-form content in 2026",
                f"https://example.com/insights/{slug}-trends-2026",
                (
                    f"Creators and brands are adopting {query.query} to improve reach "
                    "on YouTube Shorts, TikTok, and Instagram Reels."
                ),
                0.94,
                now - timedelta(days=2),
            ),
            (
                f"{query.query}: what the latest data shows",
                f"https://example.com/reports/{slug}-market-brief",
                (
                    f"A concise market brief on {query.query}, including audience demand, "
                    "competition level, and content angle opportunities."
                ),
                0.89,
                now - timedelta(days=5),
            ),
            (
                f"5 proven hooks for videos about {query.query}",
                f"https://example.com/playbooks/{slug}-hook-playbook",
                (
                    f"Practical hook patterns for {query.query} that perform well in "
                    "vertical video formats under sixty seconds."
                ),
                0.86,
                now - timedelta(days=9),
            ),
            (
                f"Expert roundup: {query.query} predictions for the next quarter",
                f"https://example.com/roundups/{slug}-outlook",
                (
                    f"Industry voices weigh in on where {query.query} is heading and "
                    "which subtopics are gaining momentum."
                ),
                0.82,
                now - timedelta(days=14),
            ),
            (
                f"Beginner's guide to {query.query} for social video",
                f"https://example.com/guides/{slug}-starter-guide",
                (
                    f"An introductory guide covering fundamentals of {query.query} "
                    "for creators publishing original short-form content."
                ),
                0.78,
                now - timedelta(days=21),
            ),
        ]

        sources = [
            ResearchSource(
                title=title,
                url=url,
                snippet=snippet,
                provider=self.name,
                published_at=published_at,
                score=score,
            )
            for title, url, snippet, score, published_at in templates[: query.max_results]
        ]

        return ResearchResult(
            query=query.query,
            sources=sources,
            provider_used=self.name,
            warnings=["Results are synthetic mock data, not live research."],
        )
